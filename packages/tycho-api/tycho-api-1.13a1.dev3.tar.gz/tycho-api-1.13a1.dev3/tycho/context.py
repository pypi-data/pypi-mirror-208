import json
import logging
import os
import requests
import requests_cache
import traceback
import uuid
import yaml
import copy
from deepmerge import Merger
from requests_cache import CachedSession
from string import Template
from jinja2 import Template as jinja2Template
from tycho.client import TychoClientFactory, TychoStatus, TychoSystem, TychoClient
from tycho.exceptions import ContextException

logger = logging.getLogger (__name__)

mixin_merge = Merger(
    [ (list,["override"]), (dict,["merge"]), (set,["union"]) ],
    ["override"],
    ["override"]
)

class Principal:
    """ Abstract representation of a system identity. """
    def __init__(self, username, a_token=None, r_token=None):
        self.username=username
        self.access_token=a_token
        self.refresh_token=r_token
        
class TychoContext:
    """
    Load, understand, and use the app registry.

    The app registry is a declarative metadata repository outlining apps available to 
    the platform. Its YAML definition structure provides 
      * Basic metadata about the registry itself including identifier, version, name, etc.
      * A list of repositories or locations apps might reference for further metadata.
      * 
    """
    
    """ https://github.com/heliumdatacommons/CommonsShare_AppStore/blob/master/CS_AppsStore/cloudtop_imagej/deployment.py """
    def __init__(self, registry_config="app-registry.yaml", app_defaults_config="app-defaults.yaml",product="common", stub=False):
        self.registry = self._get_config(registry_config)
        self.app_defaults = self._get_config(app_defaults_config)
        logger.info("defaults = ")
        logger.info(self.app_defaults)
        """ Uncomment this and related lines when this code goes live,. 
        Use a timeout on the API so the unit tests are not slowed down. """
        if not os.environ.get ('DEV_PHASE') == 'stub':
            self.client=TychoClient(url=os.environ.get('TYCHO_URL', "http://localhost:5000"))
        self.product = product
        self.apps = self._grok ()
        self.http_session = CachedSession (cache_name='tycho-registry')

    def _get_config(self, file_name):
        """ Load the registry metadata. """
        config = {}
        """ Load it from the Tycho conf directory for now. Perhaps more dynamic in the future. """
        config_path = os.path.join (
            os.path.dirname (__file__),
            "conf",
            file_name)
        with open(config_path, 'r') as stream:
            config = yaml.safe_load (stream)
        return config

    def add_conf_impl(self, apps, context):
        for key, value in context.items():
            if key in apps.keys():
                apps[key] = {**apps[key], **value}
                self.add_conf_impl(apps, value)
        return apps

    def inherit (self, contexts, context, apps={}):
        for base in context.get ("extends", []):
            self.inherit (contexts, contexts[base], apps)
        apps.update (copy.deepcopy(context.get ("apps", {})))
        return apps
    
    def mixin_defaults(self,apps):
        for app in apps:
            apps[app] = mixin_merge.merge(copy.deepcopy(apps[app]),copy.deepcopy(self.app_defaults))
    
    def mixin(self,contexts,context,apps):
        for base in context.get ("extends", []):
            self.mixin(contexts,contexts[base],apps)
        for mixer in context.get("mixin", []):
            for app in apps:
                if contexts.get(mixer,None) != None and contexts[mixer].get("apps",None) != None and contexts[mixer]["apps"].get(app,None) != None:
                    logger.info("mixing " + app)
                    apps[app] = mixin_merge.merge(copy.deepcopy(apps[app]),copy.deepcopy(contexts[mixer]["apps"].get(app))) 
        return apps

    def _grok (self):
        """ Compile the registry, resolving text substituations, etc. """
        apps = {}
        contexts = self.registry.get ('contexts', {})
        if not self.product in contexts:
            raise ContextException (f"undefined product {self.product} not found in contexts.")
        logger.info (f"-- load-context: id:{self.product}")
        '''
        context = contexts[self.product]
        apps = context.get ('apps', {})
        """ Resolve context inheritance. """
        for base_name in context.get ('extends', []):
            if not base_name in contexts:
                raise ContextException (f"base {base_name} of context {self.product} not found in registry.")
            logger.debug (f"resolving inheritance of base {base_name} by context {self.product}")
            apps.update (contexts[base_name].get('apps'))
            new_apps = contexts[base_name].get ('apps', {})
            new_apps.update (apps)
            apps = new_apps
        '''
        context = contexts[self.product]
        logger.debug (f"---------------> {context}")
        apps = self.inherit (contexts=contexts, context=context)
        self.mixin_defaults(apps)
        self.mixin(contexts,context,apps)
        """ Load the repository map to enable string interpolation. """
        repository_map = {
            key : value['url']
            for key, value in self.registry.get ('repositories', {}).items ()
        }
        """ Compile URLs to resolve repository variables. """
        for name, app in apps.items (): #context.get('apps',{}).items ():
            if not 'spec' in app:
                repos = list(repository_map.items())
                if len(repos) == 0:
                    raise ValueError ("No spec URL and no repositories specified.")
                repo_url = repos[0][1]
                dockstore_branch = os.environ.get("DOCKSTORE_APPS_BRANCH", "master")
                if dockstore_branch != "master":
                    repo_url = repo_url.replace("master", dockstore_branch)
                app['spec'] = f"{repo_url}/{name}/docker-compose.yaml"
            spec_url = app['spec']
            app['icon'] = os.path.join (os.path.dirname (spec_url), "icon.png")
            for key in [ 'spec', 'icon', 'docs' ]:
                url = app[key]
                app[key] = Template(url).safe_substitute (repository_map)
            logger.debug (f"-- spec: {app['spec']}")
            logger.debug (f"-- icon: {app['icon']}")
        logger.debug (f"-- product {self.product} resolution => apps: {apps.keys()}")
        apps = self.add_conf_impl(apps, context)
        for app, value in apps.items():
            logger.debug("app:" + app)
            logger.debug(value)
        return apps
    
    def get_definition(self, app_id):
        """ Get the apps source definition"""
        app_definition = self.apps[app_id].get('definition')
        if not app_definition:
            try:
                logger.debug (f"-- resolving definition for {app_id}")
                url = self.apps[app_id]['spec']
                response = self.http_session.get(url)
                if response.status_code != 200:
                    raise ValueError(f"-- app {app_id}. failed to parse spec. code:{response.status_code}")
                template_dict = yaml.safe_load (response.text)
                context = self.registry["settings"]
                logger.debug (f"-----> context: {context}")
                spec_template = str (template_dict)
                logger.debug (f"-----> spec_template:\n{spec_template}")
                template = jinja2Template (spec_template)
                try:
                    app_def_str = template.render(**context)
                    logger.debug (f"-----> Rendered app definition:\n{app_def_str}")

                    # Validate safety of rendered definition/convert back to dict before storing
                    app_definition = yaml.safe_load(app_def_str)
                    self.apps[app_id]['definition'] = app_definition
                except Exception as e:
                    logger.error (f"-- app {app_id} failed to render app definition.\nError: {e}")
                    logger.debug ("", exc_info=True)
                    logger.warning (f"-- Setting app {app_id} app definition to empty dict")
                    app_definition = {}
                    self.apps[app_id]['definition'] = app_definition
            except Exception as e:
                logger.error (f"-- app {app_id}. failed to parse definition.\nstatus code:{response.status_code}\nerror: {e}")
                logger.debug ("", exc_info=True)
        return app_definition

    def get_spec (self, app_id):
        """ Get the URL of the system docker-compose yaml specification. """
        spec = self.apps[app_id].get ('spec_obj', None)
        if not spec:
            url = None
            response = None
            try:
                logger.debug (f"-- resolving specification for app: {app_id}")
                url = self.apps[app_id]['spec']
                response = self.http_session.get (url)
                if response.status_code != 200:
                    raise ValueError (f"-- app {app_id}. failed to parse spec. code:{response.status_code}")
                template_dict = yaml.safe_load (response.text)
                context = self.registry["settings"]
                logger.debug (f"-----> context: {context}")
                spec_template = str (template_dict)
                logger.debug (f"-----> spec_template: {spec_template}")
                template = jinja2Template (spec_template)
                try:
                    spec_str = template.render(**context)
                    logger.debug (f"-----> rendered spec:\n{spec_str}")

                    # Validate spec/convert spec to a dict before storing
                    spec = yaml.safe_load (spec_str)
                    self.apps[app_id]['spec_obj'] = spec
                except Exception as e:
                    traceback.print_exc ()
                    logger.error (f"--  app {app_id}.\n Failed to render spec.\nError: {e}")
            except Exception as e:
                traceback.print_exc ()
                if response:
                    logger.error (f"-- app {app_id}. failed to parse spec. code:{response.status_code}")
                else:
                    logger.error (f"-- app {app_id}. failed to parse spec.")
                raise e
        else:
             try:
                 logger.debug(f"-- removing cached volumes")
                 spec['services'][app_id].pop('volumes', None)
             except Exception as e:
                 traceback.print_exc ()
                 logger.error (f"-- app {app_id}. failed to remove cached volumes in parse spec.")
                 raise e
        return spec

    def get_env_registry(self, app_id, settings):
        """ Get the env variables specified for an app in the registry and update settings"""
        env = self.apps[app_id].get('env', None)
        if env:
            settings.update(env)
        return settings
    
    def get_settings (self, app_id):
        """ Get the URL of the .env settings / environment file. """
        env = self.apps[app_id].get ('env_obj', None)
        if not env:
            url = self.apps[app_id]['spec']
            env_url = os.path.join (os.path.dirname (url), ".env")
            logger.debug (f"-- resolving settings for app: {app_id}")
            response = self.http_session.get (env_url)
            if response.status_code == 200:
                logger.debug (f"-- got settings for {app_id}")
                env = response.text
            else:
                logger.debug (f"-- using empty settings for {app_id}")
                env = ""
            self.apps[app_id]['env_obj'] = env
        return env

    def status (self, request):
        return self.client.status (request)

    def delete (self, request):
        return self.client.delete (request)

    def update(self, request):
        return self.client.patch(request)
    
    def start (self, principal, app_id, resource_request, host):
        """ Get application metadata, docker-compose structure, settings, and compose API request. """
        spec = self.get_spec (app_id)
        settings = self.client.parse_env (self.get_settings (app_id))
        settings_all = self.get_env_registry(app_id, settings)
        services = self.apps[app_id]['services']
        services = { k : {
            "port" : str(v),
            "clients" : []
          } for k, v in services.items ()
        }
        logger.debug (f"parsed {app_id} settings: {settings}")
        """ Use a pre-existing k8s service account """
        service_account = self.apps[app_id]['serviceAccount'] if 'serviceAccount' in self.apps[app_id].keys() else None
        """ Add entity's auth information """
        principal_params = {"username": principal.username, "access_token": principal.access_token, "refresh_token": principal.refresh_token, "host": host}
        principal_params_json = json.dumps(principal_params, indent=4)
        """ Security Context that are set for the app """
        spec["security_context"] = self.apps[app_id]["securityContext"] if 'securityContext' in self.apps[app_id].keys() else {}
        spec["services"][app_id]["ext"] = self.apps[app_id]["ext"] if 'ext' in self.apps[app_id].keys() else None
        spec["services"][app_id].update(resource_request)
        """ Certain apps might require appending a string to the custom URL. """
        conn_string = self.apps.get(app_id).get("conn_string", "")
        spec["services"][app_id]["conn_string"] = conn_string
        """ Add a proxy rewrite rule """
        proxy_rewrite_rule = self.apps.get(app_id).get("proxy-rewrite-rule", False)
        spec["services"][app_id]["proxy_rewrite_rule"] = proxy_rewrite_rule

        if spec is not None:
            system = self._start ({
                "name"       : app_id,
                "serviceaccount": service_account,
                "env"        : settings_all,
                "system"     : spec,
                "principal"   : principal_params_json,
                "services"   : services
            })
            """ Validate resulting interfaces. """
            """
            TODO: 
              1. Check returned status.
              2. The Ambassador based URL removes the need to pass back a port. Confirm & delete port code.
            """
            running = { v.name : v.port for v in system.services }
            for name, port in services.items ():
                assert name in running, f"Svc {name} expected but {services.keys()} actually running."            
            logger.info (
                f"  -- started app id:{app_id} user:{principal.username} id:{system.identifier} services:{list(running.items ())}")
        return system
    
    def _start (self, request):
        """
        Control low level application launching (start) logic. 
        Also provides an anchor point to mock the service in unit tests.
        """
        return self.client.start (request)

class NullContext (TychoContext):
    """
    A null context to facilitate client development.
    """
    def __init__(self,product="common"):
        super ().__init__(product=product,stub=True)

    def status(self, request=None):
        """ Make up some rows. """
        identifier = uuid.uuid4 ()
        return TychoStatus (**{
            "status" : "success",
            "result" : [
                {
                    "name"          : f"jupyter-ds-{str(identifier)}",
                    "app_id"        : "jupyter-ds",
                    "sid"           : str(identifier),
                    "ip_address"    : 'x.y.z.m',
                    "port"          : "8080",
                    "creation_time" : "time"
                } for x in range(8000, 8005)
            ],
            "message" : "..."
        })

    def delete (self, request):
        """ Ingore deletes. """
        logger.debug (f"-- delete: {request}")
        
    def start (self, principal, app_id):
        logger.debug (f"-- start: {principal} {app_id}")        
        spec = self.get_spec (app_id)
        #settings = self.client.parse_env (self.get_settings (app_id))
        settings = self._parse_env (self.get_settings (app_id))
        services = self.apps[app_id]['services']
        return TychoSystem (**{
        "status" : "ok",
        "result" : {
            "name"       : self.apps[app_id]['name'],
            "sid"        : uuid.uuid4 (),
            "containers" :  {
                k : { 'ip_address' : 'x.y.z', 'port-1' : v }
                for k, v in services.items ()
            }
        },
        "message" : "mock: testing..."
    })
    
class ContextFactory:
    """ Flexible method for connecting to a TychoContext.
    Also, provide the null context for easy dev testing in appstore. """
    @staticmethod
    def get (product, context_type="null"):
        return {
            "null" : NullContext(product=product),
            "live" : TychoContext(product=product)
        }[context_type]
    
            
        

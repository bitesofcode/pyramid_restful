"""
ORB stands for Object Relation Builder and is a powerful yet simple to use \
database class generator.
"""

# auto-generated version file from releasing
try:
    from ._version import __major__, __minor__, __revision__, __hash__
except ImportError:
    __major__ = 0
    __minor__ = 0
    __revision__ = 0
    __hash__ = ''

__version_info__ = (__major__, __minor__, __revision__)
__version__ = '{0}.{1}.{2}'.format(*__version_info__)


from .endpoint import *


def includeme(config):
    # define a new renderer for json
    config.add_renderer('json2', factory='pyramid_restful.renderer.json2_renderer_factory')

    settings = config.registry.settings

    # create the API factory
    api_root = settings.get('restful.api.root')

    if api_root:
        from .api import ApiFactory

        # setup cross-origin support
        cors_options = {
            k.replace('restful.cors.', ''): v
            for k, v in settings.items()
            if k.startswith('restful.cors.')
        }

        api = ApiFactory(
            application=settings.get('restful.application', 'pyramid_orb'),
            version=settings.get('restful.api.version', '1.0.0'),
            cors_options=cors_options or None
        )

        permission = settings.get('restful.api.permission')
        api.serve(config, api_root, route_name='restful.api', permission=permission)

        # store the API instance on the configuration
        config.registry.rest_api = api

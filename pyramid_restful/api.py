import inspect
import projex.text

from pyramid.httpexceptions import HTTPForbidden
from .services import *
from .decorators import *


class ApiFactory(dict):
    def __init__(self, version='1.0.0', authorization_policy=None):
        super(ApiFactory, self).__init__()

        # custom properties
        self.__authorization_policy = authorization_policy
        self.__version = version

        # services
        self.__services = {}

    def factory(self, request, parent=None, name=None):
        """
        Returns a new service for the given request.

        :param      request | <pyramid.request.Request>

        :return     <pyramid_restful.services.AbstractService>
        """
        service = AbstractService(request)
        for name, (service_type, service_object) in self.__services.items():
            if service_object is None:
                service[name] = service_type(request, parent=service, name=name)
            else:
                service[name] = service_type(request, service_object, parent=service, name=name)

        request.api_service = service
        return service

    def process(self, request):
        # look for a request to the root of the API, this will generate the
        # help information for the system
        if not request.traversed:
            return {}

        # otherwise, process the request context
        else:
            i = request.registry.introspector.get('authorization policy', None)
            if i is not None:
                policy = i['policy']
                if not policy.permits(request.context, request.effective_principals, request.context.permission()):
                    raise HTTPForbidden()

            return request.context.process()

    def register(self, service, name=''):
        """
        Exposes a given service to this API.
        """
        # expose a sub-factory
        if isinstance(service, ApiFactory):
            self.__services[name] = (service.factory, None)

        # expose a sub-service
        elif isinstance(service, AbstractService):
            name = name or service.__name__
            self.__services[name] = (service, None)

        # expose a module dynamically as a service
        elif inspect.ismodule(service):
            name = name or service.__name__.split('.')[-1]
            self.__services[name] = (ModuleService, service)

        # expose a class dynamically as a service
        elif inspect.isclass(service):
            name = name or service.__name__
            self.__services[name] = (ClassService, service)

        # expose a function dynamically as a service
        elif inspect.isfunction(service):
            name = name or service.__name__
            self.__services[name] = (FunctionService, service)

        # expose a service directly
        else:
            raise StandardError('Invalid service provided.')

    def handle_error(self, request):
        err = request.exception
        status = getattr(err, 'status', projex.text.pretty(type(err).__name__))
        code = getattr(err, 'code', 500)

        request.response.status = '{0} {1}'.format(code, status)

        return {'error': projex.text.nativestring(err)}

    def serve(self, config, path, route_name=None, **view_options):
        """
        Serves this API from the inputted root path
        """
        route_name = route_name or path.replace('/', '.').strip('.')
        path = path.strip('/') + '/*traverse'

        # configure the route and the path
        config.add_route(route_name, path, factory=self.factory)
        config.add_view(
            self.process,
            route_name=route_name,
            renderer='json2',
            accept='application/json',
            **view_options
        )
        # config.add_view(
        #     self.handle_error,
        #     route_name=route_name,
        #     renderer='json2',
        #     accept='application/json',
        #     context=StandardError
        # )


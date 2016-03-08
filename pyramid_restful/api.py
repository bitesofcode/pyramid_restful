import inspect
import logging
import projex.text
import textwrap

from pyramid.response import Response
from pyramid.httpexceptions import HTTPNotFound
from collections import defaultdict

from .documentation import Documentation, SectionGroup, Section
from .services import *

log = logging.getLogger(__name__)


class ApiFactory(dict):
    def __init__(self,
                 version='1.0.0',
                 application='pyramid_restful',
                 documentation_package='pyramid_restful',
                 documentation_folder='templates',
                 documentation_template='documentation.html.jinja'):
        super(ApiFactory, self).__init__()

        # custom properties
        self.__version = version
        self.__application = application
        self.__documentation = Documentation(documentation_package, documentation_folder, documentation_template)

        # services
        self.__services = {}

    def application(self):
        return self.__application

    def collect_documentation(self, name, service_info):
        service, service_object = service_info

        if issubclass(service, ModuleService):
            module_name = service_object.__name__.split('.')[-1]
            group_name = getattr(service_object, '__group__', 'Topics')
            docs = getattr(service_object, '__doc__', '') or ''

            methods = [(docs, '')]

            for method in vars(service_object).values():
                if isinstance(method, CallableService):
                    method_doc = '## {0}\n\n'.format(method.__name__)
                    method_doc += textwrap.dedent(getattr(method, '__doc__', '')) or ''
                    methods.append((method_doc, ''))

            section = Section(
                id=module_name,
                name=getattr(service_object, '__title__', module_name),
                methods=methods
            )
            yield group_name, section

    def cors_setup(self, request):
        response = Response()
        if request.is_xhr:
            response.headerlist = []
            response.headerlist.extend(
                (
                    ('Access-Control-Allow-Origin', '*'),
                    ('Content-Type', 'application/json')
                )
            )
        return response

    def factory(self, request, parent=None, name=None):
        """
        Returns a new service for the given request.

        :param      request | <pyramid.request.Request>

        :return     <pyramid_restful.services.AbstractService>
        """
        # show documentation at the root path
        if not request.matchdict['traverse']:
            return {}
        else:
            name = name or request.matchdict['traverse'][0]

            service = AbstractService(request)
            try:
                service_type, service_object = self.__services[name]
            except KeyError:
                raise HTTPNotFound()
            else:
                if service_object is None:
                    service[name] = service_type(request, parent=service, name=name)
                else:
                    service[name] = service_type(request, service_object, parent=service, name=name)

            request.api_service = service
            return service

    def process(self, request):
        if request.method.lower() == 'options':
            return self.cors_setup(request)

        # look for a request to the root of the API, this will generate the
        # help information for the system
        elif not request.traversed:
            if 'application/json' not in request.accept.header_value:
                body = self.__documentation.render(self, request)
                return Response(body=body)
            else:
                return {'version': self.__version}

        # otherwise, process the request context
        else:
            permit = request.context.permission()
            if permit and not request.has_permission(permit):
                HTTPForbidden()
            else:
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

        log.exception(err)

        status = getattr(err, 'status', projex.text.pretty(type(err).__name__))
        code = getattr(err, 'code', 500)

        request.response.status = '{0} {1}'.format(code, status)

        return {
            'type': projex.text.underscore(projex.text.underscore(type(err).__name__)),
            'error': projex.text.nativestring(err)
        }

    def section_groups(self, request):
        intro = self.__documentation.introduction(self, request)

        section_group = SectionGroup(
            name='Introduction',
            sections=[intro]
        )

        section_groups = [section_group]
        sections = defaultdict(list)

        for name, service_info in sorted(self.__services.items()):
            for group_name, section in self.collect_documentation(name, service_info):
                sections[group_name].append(section)

        # show topics first
        topics = sections.pop('Topics', [])
        if topics:
            section_groups.append(SectionGroup(
                name='Topics',
                sections=topics
            ))

        # show core resources second
        resources = sections.pop('Core Resources', [])
        if resources:
            section_groups.append(SectionGroup(
                name='Core Resources',
                sections=resources
            ))

        # show all other topics
        for group_name, sections in sorted(sections.items()):
            section_groups.append(SectionGroup(
                name=group_name,
                sections=sections
            ))

        return section_groups

    def serve(self, config, path, route_name=None, **view_options):
        """
        Serves this API from the inputted root path
        """
        route_name = route_name or path.replace('/', '.').strip('.')
        path = path.strip('/') + '*traverse'

        self.route_name = route_name

        # configure the route and the path
        config.add_route(route_name, path, factory=self.factory)
        config.add_view(
            self.handle_error,
            route_name=route_name,
            renderer='json2',
            accept='application/json',
            context=StandardError
        )
        config.add_view(
            self.process,
            route_name=route_name,
            renderer='json2',
            accept='application/json',
            **view_options
        )


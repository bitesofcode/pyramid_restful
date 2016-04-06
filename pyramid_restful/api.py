import inspect
import logging
import projex.text
import textwrap

from collections import defaultdict
from pyramid.view import view_config
from pyramid.httpexceptions import HTTPNotFound, HTTPForbidden, HTTPException
from pyramid.response import Response

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

        # private properties
        self.__documentation = Documentation(documentation_package, documentation_folder, documentation_template)

        # public properties
        self.version = version
        self.application = application
        self.services = {}

    def collect_documentation(self, name, service_info):
        service, service_object = service_info

        try:
            is_module = issubclass(service, ModuleService)
        except StandardError:
            is_module = False

        if is_module:
            module_name = service_object.__name__.split('.')[-1]
            group_name = getattr(service_object, '__group__', 'Topics')
            docs = getattr(service_object, '__doc__', '') or ''

            methods = [(docs, '')]

            for method in vars(service_object).values():
                if isinstance(service, Endpoint):
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

            service = {}
            try:
                service_type, service_object = self.services[name]
            except KeyError:
                raise HTTPNotFound()
            else:
                if isinstance(service_type, Endpoint):
                    service[name] = service_type
                elif service_object is None:
                    service[name] = service_type(request)
                else:
                    service[name] = service_type(request, service_object)

            request.api_service = service
            return service

    def process(self, request):
        if request.method.lower() == 'options':
            return self.cors_setup(request)

        # look for a request to the root of the API, this will generate the
        # help information for the system
        elif not request.traversed:
            try:
                accept = request.accept.header_value
            except StandardError:
                accept = 'text/html'

            if 'application/json' not in accept:
                body = self.__documentation.render(self, request)
                return Response(body=body)
            else:
                return {'application': self.application, 'version': self.version}

        # otherwise, process the request context
        else:
            caller = request.context
            method = request.method.lower()

            # process an endpoint function
            if isinstance(caller, Endpoint):
                method = request.method.lower()
                try:
                    permit = caller.permissions[method]
                    callable = caller.callables[method]
                except KeyError:
                    raise HTTPNotFound()
                else:
                    print permit, request.has_permission(permit)
                    if permit and not request.has_permission(permit):
                        raise HTTPForbidden()
                    else:
                        return callable(request)

            # process an endpoint method
            elif inspect.ismethod(caller) and isinstance(getattr(caller.im_func, 'endpoint', None), Endpoint):
                try:
                    permit = caller.im_func.endpoint.permissions[method]
                except KeyError:
                    raise HTTPNotFound()
                else:
                    if permit and not request.has_permission(permit):
                        raise HTTPForbidden()
                    else:
                        return caller()

            # check if the caller has its own built-in process
            elif hasattr(caller, 'process'):
                return caller.process()

            else:
                raise HTTPNotFound()


    def register(self, service, name=''):
        """
        Exposes a given service to this API.
        """
        # expose a sub-factory
        if isinstance(service, ApiFactory):
            self.services[name] = (service.factory, None)

        # expose a module dynamically as a service
        elif inspect.ismodule(service):
            name = name or service.__name__.split('.')[-1]
            self.services[name] = (ModuleService, service)

        # expose a class dynamically as a service
        elif inspect.isclass(service):
            name = name or service.__name__
            self.services[name] = (ClassService, service)

        # expose an endpoint directly
        elif isinstance(getattr(service, 'endpoint', None), Endpoint):
            self.services[service.endpoint.name] = (service.endpoint, None)

        # expose a service directly
        else:
            raise StandardError('Invalid service provide: {0} ({1}).'.format(service, type(service)))

    @view_config(context=StandardError, accept='application/json', renderer='json2')
    @view_config(context=HTTPException, accept='application/json', renderer='json2')
    def handle_error(self, request):
        err = request.exception

        log.exception(err)

        status = getattr(err, 'status', projex.text.pretty(type(err).__name__))
        code = getattr(err, 'code', 500)

        request.response.status = '{0} {1}'.format(code, status)

        # for 500 errors, only return server error
        if code / 100 == 5:
            return {
                'type': 'server_error',
                'error': 'An unknown server error occurred.'
            }
        else:
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

        for name, service_info in sorted(self.services.items()):
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
            self.process,
            route_name=route_name,
            renderer='json2',
            **view_options
        )
        config.scan()


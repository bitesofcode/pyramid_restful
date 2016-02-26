from .services import CallableService
from pyramid.httpexceptions import HTTPForbidden


def acl(permission):
    def wrapper(function):
        def proxy(record, *args, **kwds):
            ctxt = record.context()
            r = ctxt.scope.get('request')
            if r:
                i = r.registry.introspector.get('authorization policy', None)
                if i is not None:
                    policy = i['policy']
                    if not policy.permits(r.context, r.effective_principals, permission):
                        raise HTTPForbidden()

            return function(record, *args, **kwds)
        return proxy
    return wrapper


class endpoint(object):
    @staticmethod
    def get(**options):
        def setup(callable):
            name = options.pop('name', callable.__name__)
            return CallableService(name,
                                   callable,
                                   method='GET',
                                   permission=options.pop('permission', '__DEFAULT__'))
        return setup

    @staticmethod
    def post(**options):
        def setup(callable):
            name = options.pop('name', callable.__name__)
            return CallableService(name,
                                   callable,
                                   method='POST',
                                   permission=options.pop('permission', '__DEFAULT__'))
        return setup

    @staticmethod
    def delete(**options):
        def setup(callable):
            name = options.pop('name', callable.__name__)
            return CallableService(name,
                                   callable,
                                   method='DELETE',
                                   permission=options.pop('permission', '__DEFAULT__'))
        return setup

    @staticmethod
    def put(**options):
        def setup(callable):
            name = options.pop('name', callable.__name__)
            return CallableService(name,
                                   callable,
                                   method='PUT',
                                   permission=options.pop('permission', '__DEFAULT__'))
        return setup

    @staticmethod
    def patch(**options):
        def setup(callable):
            name = options.pop('name', callable.__name__)
            return CallableService(name,
                                   callable,
                                   method='PATCH',
                                   permission=options.pop('permission', '__DEFAULT__'))
        return setup

class Endpoint(object):

    def __init__(self, callable, name='', method='get', permission=None, pattern=None, action=None):
        self.name = name or callable.__name__
        self.callables = {}
        self.permissions = {}
        self.pattern = pattern
        self._setup(callable, method=method, permission=permission)

    def _setup(self, callable, method='get', permission=None, action=None):

        if action:
            setattr(self.callables[method.lower()], action, callable)

        else:
            self.callables[method.lower()] = callable

        self.permissions[method.lower()] = permission
        callable.endpoint = self

        return callable

    def action(self, name=None, permission=None, method='get'):
        def setup(callable):
            if name is None:
                action_name = callable.__name__
            else:
                action_name = name
            return self._setup(callable,
                               method=method,
                               permission=permission,
                               action=action_name)
        return setup

    def method(self, method='get', permission=None):
        def setup(callable):
            return self._setup(callable, method=method, permission=permission)
        return setup

    def get(self, permission=None):
        def setup(callable):
            return self._setup(callable, method='get', permission=permission)
        return setup

    def post(self, permission=None):
        def setup(callable):
            return self._setup(callable, method='post', permission=permission)
        return setup

    def delete(self, permission=None):
        def setup(callable):
            return self._setup(callable, method='delete', permission=permission)
        return setup

    def patch(self, permission=None):
        def setup(callable):
            return self._setup(callable, method='patch', permission=permission)
        return setup

    def put(self, permission=None):
        def setup(callable):
            return self._setup(callable, method='put', permission=permission)
        return setup


class endpoint(object):

    @staticmethod
    def action(method='get', name=None, **options):

        def setup(callable):
            if name is None:
                action_name = callable.__name__
            else:
                action_name = name
            Endpoint(callable, action=action_name, method=method, **options)
            return callable
        return setup

    @staticmethod
    def method(method='get', **options):
        def setup(callable):
            Endpoint(callable, method=method, **options)
            return callable
        return setup

    @staticmethod
    def get(**options):
        def setup(callable):
            Endpoint(callable, method='get', **options)
            return callable
        return setup

    @staticmethod
    def post(**options):
        def setup(callable):
            Endpoint(callable, method='post', **options)
            return callable
        return setup

    @staticmethod
    def delete(**options):
        def setup(callable):
            Endpoint(callable, method='delete', **options)
            return callable
        return setup

    @staticmethod
    def put(**options):
        def setup(callable):
            Endpoint(callable, method='put', **options)
            return callable
        return setup

    @staticmethod
    def patch(**options):
        def setup(callable):
            Endpoint(callable, method='patch', **options)
            return callable
        return setup

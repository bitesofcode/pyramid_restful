from .endpoint import Endpoint


class ModuleService(object):
    def __init__(self, request, module):
        self.request = request
        self.module = module

    def __getitem__(self, key):
        try:
            function = getattr(self.module, key)
        except AttributeError:
            raise KeyError
        else:
            if isinstance(getattr(function, 'endpoint', None), Endpoint):
                return function.endpoint
            else:
                raise KeyError


class ClassService(object):
    def __init__(self, request, cls):
        self.request = request
        self.instance = cls(request)

    def __getitem__(self, key):
        try:
            method = getattr(self.instance, key)
        except AttributeError:
            raise KeyError
        else:
            if isinstance(getattr(method.im_func, 'endpoint', None), Endpoint):
                match = method.im_func.endpoint.callables[self.instance.request.method.lower()]
                return getattr(self.instance, match.__name__)
            else:
                raise KeyError

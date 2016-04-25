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

    @classmethod
    def routes(cls, obj):
        root = obj.__name__.split('.')[-1]
        output = {}
        for value in vars(obj):
            if isinstance(getattr(value, 'endpoint', None), Endpoint):
                output['/{0}/{1}'.format(root, value.name)] = ','.join(sorted(value.callables.keys()))
        return output


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

    @classmethod
    def routes(cls, obj):
        output = {}
        for value in vars(obj):
            if isinstance(getattr(value.im_func, 'endpoint', None), Endpoint):
                output['/{0}/{1}'.format(root, value.name)] = ','.join(sorted(value.callables.keys()))
        return output
from .services import CallableService


class endpoint(object):
    @staticmethod
    def get(**options):
        def setup(callable):
            name = options.pop('name', callable.__name__)
            return CallableService(name,
                                   callable,
                                   method='GET',
                                   permission=options.pop('permission', None))
        return setup

    @staticmethod
    def post(**options):
        def setup(callable):
            name = options.pop('name', callable.__name__)
            return CallableService(name,
                                   callable,
                                   method='POST',
                                   permission=options.pop('permission', None))
        return setup

    @staticmethod
    def delete(**options):
        def setup(callable):
            name = options.pop('name', callable.__name__)
            return CallableService(name,
                                   callable,
                                   method='DELETE',
                                   permission=options.pop('permission', None))
        return setup

    @staticmethod
    def put(**options):
        def setup(callable):
            name = options.pop('name', callable.__name__)
            return CallableService(name,
                                   callable,
                                   method='PUT',
                                   permission=options.pop('permission', None))
        return setup

    @staticmethod
    def patch(**options):
        def setup(callable):
            name = options.pop('name', callable.__name__)
            return CallableService(name,
                                   callable,
                                   method='PATCH',
                                   permission=options.pop('permission', None))
        return setup
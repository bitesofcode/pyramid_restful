

class AbstractService(dict):
    """ Base class for all REST services used within a Pyramid Traversal """
    def __init__(self, request=None, parent=None, name=None):
        super(AbstractService, self).__init__()

        self.request = request
        self.__name__ = name or type(self).__name__
        self.__parent__ = parent

    def add(self, service):
        """
        Adds a sub-service to this instance.  This will store the given service as a sub-tree for this instance.

        :param      service | subclass of <pyramid_restful.services.AbstractService>
        """
        service.__parent__ = self
        self[service.__name__] = service

    def remove(self, service):
        """
        Removes the given service from the list of sub-services available.

        :param      service | <str> || <pyramid_restful.services.Service>
        """
        try:
            service = self.pop(service.__name__, None)
        except AttributeError:
            service = self.pop(service, None)

        if service:
            service.__parent__ = None

    def process(self):
        raise NotImplementedError

    def permission(self):
        raise NotImplementedError
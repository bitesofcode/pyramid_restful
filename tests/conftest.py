import pytest

_USER = None
_USER2 = None

@pytest.fixture()
def basics(pyramid_config):
    from pyramid_restful import endpoint

    # login resource
    @endpoint.get()
    def login(request):
        global _USER
        return _USER

    @login.endpoint.post()
    def set_login(request):
        global _USER
        _USER = {'username': request.params.get('username')}
        return _USER

    @login.endpoint.delete()
    def unset_login(request):
        global _USER
        _USER = None

    # define all endpoint options
    @endpoint.post()
    def test_post(request):
        return {}

    @endpoint.patch()
    def test_patch(request):
        return {}

    @endpoint.put()
    def test_put(request):
        return {}

    @endpoint.delete()
    def test_delete(request):
        return {}

    @endpoint.method('get')
    def test_get(request):
        return {}

    # define all verb options
    @endpoint.get()
    def test_verbs(request):
        return {}

    @test_verbs.endpoint.post()
    def test_post_verbs(request):
        return {}

    @test_verbs.endpoint.patch()
    def test_patch_verbs(request):
        return {}

    @test_verbs.endpoint.put()
    def test_put_verbs(request):
        return {}

    @test_verbs.endpoint.delete()
    def test_delete_verbs(request):
        return {}

    @test_verbs.endpoint.method('get')
    def test_method_get(request):
        return {}

    @test_verbs.endpoint.get()
    def test_verb_get(request):
        return {}

    @endpoint.post()
    def server_error(request):
        raise StandardError('This is not visible.')

    @endpoint.get(pattern='/path/to/somewhere')
    def somewhere(request):
        return 'somewhere'

    @somewhere.endpoint.post()
    def creating_somewhere(request):
        return 'creating somewhere'

    @somewhere.endpoint.action(method='post')
    def run(request):
        return 'run action'

    @endpoint.get(pattern='/path/to/somewhere/{id}')
    def getting_somewhere(request):
        return 'somewhere {0}'.format(request.matchdict['id'])

    api = pyramid_config.registry.rest_api

    api.register(login)

    api.register(test_post)
    api.register(test_patch)
    api.register(test_put)
    api.register(test_delete)
    api.register(test_get)
    api.register(server_error)
    api.register(somewhere)
    api.register(getting_somewhere)

    api.register(test_verbs)

    return api

@pytest.fixture()
def classes(pyramid_config):
    from pyramid_restful import endpoint

    class auth(object):
        def __init__(self, request):
            self.request = request

        def unexposed(self):
            return {}

        @endpoint.get()
        def login(self):
            global _USER
            return _USER

        @login.endpoint.post()
        def set_login(self):
            global _USER
            _USER = {'username': self.request.params.get('username')}
            return _USER

        @login.endpoint.delete()
        def unset_login(self):
            global _USER
            _USER = None

        @login.endpoint.action()
        def reset(self):
            return 'reset'

    api = pyramid_config.registry.rest_api
    api.register(auth)
    return api

@pytest.fixture()
def modules(pyramid_config):
    from tests import oauth
    api = pyramid_config.registry.rest_api
    api.register(oauth)
    return api

@pytest.fixture()
def authenticated(pyramid_config):
    from pyramid_restful import endpoint
    from pyramid import security

    @endpoint.get(name='login2', permission=security.Authenticated)
    def login(request):
        global _USER2
        return _USER2

    @login.endpoint.post()
    def set_login(request):
        global _USER2
        _USER2 = {'username': request.params.get('username')}
        return _USER2

    @login.endpoint.delete(permission=security.Authenticated)
    def unset_login(request):
        global _USER2
        _USER2 = None

    api = pyramid_config.registry.rest_api
    api.register(login)
    return api


@pytest.fixture()
def logged_out(authenticated, pyramid_config):
    from pyramid.testing import DummySecurityPolicy

    class CustomDummySecurityPolicy(DummySecurityPolicy):
        def permits(self, context, principals, permission):
            return permission in principals

    policy = CustomDummySecurityPolicy()

    pyramid_config.set_authentication_policy(policy)
    pyramid_config.set_authorization_policy(policy)

    return policy

@pytest.fixture()
def logged_in(logged_out):
    logged_out.userid = 1
    return logged_out

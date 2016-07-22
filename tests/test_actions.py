import logging

from pyramid_restful import endpoint

logging.basicConfig()


def test_attaching_action():

    @endpoint.get()
    def some_get():
        return 'foo'

    @some_get.endpoint.action()
    def run():
        return 'run'

    assert some_get.run is run

    @endpoint.get()
    def some_get_b():
        return 'bar'

    @some_get_b.endpoint.action(name='doit')
    def run_2():
        return 'yop'

    assert some_get_b.doit is run_2


def test_attaching_method_action():

    class MyClass(object):

        @endpoint.post()
        def some_get(self):
            return 'foo'

        @some_get.endpoint.action(method='post')
        def run(self):
            return 'run'

    my_instance = MyClass()
    assert my_instance.some_get.run.__name__ == my_instance.run.__name__
    assert my_instance.some_get.run(my_instance) == 'run'


def test_action_endpoint(basics, pyramid_app):
    r = pyramid_app.post('/api/v1/path/to/somewhere')
    assert r.json == 'creating somewhere'

    r = pyramid_app.post('/api/v1/path/to/somewhere?action=run')
    assert r.json == 'run action'


def test_class_action_endpoint(classes, pyramid_app):
    r = pyramid_app.get('/api/v1/auth/login?action=reset')
    assert r.json == 'reset'


def test_action_argument(basics, pyramid_app):
    '''
    Test posting to an endpoint which takes an argument named 'action' but
    doesn't have an action callback attached.
    '''
    r = pyramid_app.get('/api/v1/path/to/somewhere?action=foo')
    assert r.json == 'somewhere'

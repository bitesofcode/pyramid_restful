from pyramid_restful import endpoint


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


def test_action_endpoint(basics, pyramid_app):
    r = pyramid_app.post('/api/v1/path/to/somewhere')
    assert r.json == 'creating somewhere'

    r = pyramid_app.post('/api/v1/path/to/somewhere?action=run')
    assert r.json == 'run action'

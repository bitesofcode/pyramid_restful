import pytest

def test_put_login_from_class_not_found(basics, pyramid_app):
    r = pyramid_app.put('/api/v1/login', params='username=bob', expect_errors=True)
    assert r.status_code == 404

def test_get_null_login(basics, pyramid_app):
    r = pyramid_app.get('/api/v1/login')
    assert r.json is None

def test_set_new_login(basics, pyramid_app):
    r = pyramid_app.post('/api/v1/login', params='username=me@here.com&password=blah')
    assert r.json['username'] == 'me@here.com'

def test_get_updated_login(basics, pyramid_app):
    r = pyramid_app.get('/api/v1/login')
    assert r.json is not None
    assert r.json['username'] == 'me@here.com'

def test_unset_login(basics, pyramid_app):
    r = pyramid_app.delete('/api/v1/login')
    assert r.json is None

    r = pyramid_app.get('/api/v1/login')
    assert r.json is None

def test_all_routes(basics, pyramid_app):
    for method in ('get', 'post', 'patch', 'put', 'delete'):
        func = getattr(pyramid_app, method)
        r = func('/api/v1/test_{0}'.format(method))
        assert r.status_code == 200

def test_all_verbs(basics, pyramid_app):
    for method in ('get', 'post', 'patch', 'put', 'delete'):
        func = getattr(pyramid_app, method)
        r = func('/api/v1/test_verbs')
        assert r.status_code == 200
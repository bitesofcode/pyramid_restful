import pytest

def test_put_login_from_module_not_found(modules, pyramid_app):
    r = pyramid_app.put('/api/v1/oauth/login', params='username=bob', expect_errors=True)
    assert r.status_code == 404

def test_invalid_module_path(modules, pyramid_app):
    r = pyramid_app.get('/api/v1/oauth/missing', expect_errors=True)
    assert r.status_code == 404

def test_invalid_module_method(modules, pyramid_app):
    r = pyramid_app.get('/api/v1/oauth/unexposed', expect_errors=True)
    assert r.status_code == 404

def test_get_null_login_from_module(modules, pyramid_app):
    r = pyramid_app.get('/api/v1/oauth/login')
    assert r.json is None

def test_set_new_login_from_class(modules, pyramid_app):
    r = pyramid_app.post('/api/v1/oauth/login', params='username=me@here.com&password=blah')
    assert r.json['username'] == 'me@here.com'

def test_get_updated_login_from_class(modules, pyramid_app):
    r = pyramid_app.get('/api/v1/oauth/login')
    assert r.json is not None
    assert r.json['username'] == 'me@here.com'

def test_unset_login_from_class(modules, pyramid_app):
    r = pyramid_app.delete('/api/v1/oauth/login')
    assert r.json is None

    r = pyramid_app.get('/api/v1/oauth/login')
    assert r.json is None

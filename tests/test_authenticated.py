import pytest

def test_get_null_login_authenticated_failure(logged_out, pyramid_app):
    r = pyramid_app.get('/api/v1/login2', expect_errors=True)
    assert r.status_code == 403

def test_set_new_login_authenticated_success(logged_out, pyramid_app):
    r = pyramid_app.post('/api/v1/login2', params='username=me@here.com&password=blah')
    assert r.status_code == 200
    assert r.json['username'] == 'me@here.com'

def test_get_updated_login_authenticated_success(logged_in, pyramid_app):
    r = pyramid_app.get('/api/v1/login2')
    assert r.status_code == 200

def test_get_updated_login_authenticated_failure(logged_out, pyramid_app):
    r = pyramid_app.get('/api/v1/login2', expect_errors=True)
    assert r.status_code == 403

def test_unset_login_authenticated_success(logged_in, pyramid_app):
    r = pyramid_app.delete('/api/v1/login2')
    assert r.status_code == 200

def test_unset_login_authenticated_failure(logged_out, pyramid_app):
    r = pyramid_app.delete('/api/v1/login2', expect_errors=True)
    assert r.status_code == 403
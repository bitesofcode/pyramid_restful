import pytest

def test_get_version(pyramid_app):
    r = pyramid_app.get('/api/v1', headers={'Accept': 'application/json'})
    assert r.json['version'] == '0.0.1'

def test_get_bad_url(pyramid_app):
    r = pyramid_app.get('/api/v1/users/1', expect_errors=True)

    # ensure the route does not exist
    assert r.status_code == 404

def test_get_docs(basics, modules, classes, pyramid_app):
    r = pyramid_app.get('/api/v1', headers={'Accept': 'text/html'})
    assert r.html is not None

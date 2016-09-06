import pytest


def test_payload_parsing_for_params():
    from pyramid.testing import DummyRequest
    from webob.multidict import NestedMultiDict
    from pyramid_restful.utils import get_payload

    request = DummyRequest(NestedMultiDict({'test_param': '10'}))

    assert request.params.get('test_param') == '10'
    with pytest.raises(AttributeError):
        body = request.json_body

    data = get_payload(request)

    assert len(data) == 1
    assert data['test_param'] == '10'

def test_payload_parsing_for_json():
    from pyramid.testing import DummyRequest
    from webob.multidict import NestedMultiDict
    from pyramid_restful.utils import get_payload

    request = DummyRequest(NestedMultiDict())
    setattr(request, 'json_body', {'test_param': '10'})

    assert request.params.get('test_param') is None
    assert request.json_body.get('test_param') == '10'

    data = get_payload(request)

    assert len(data) == 1
    assert data['test_param'] == '10'

def test_payload_parsing_for_mixed():
    from pyramid.testing import DummyRequest
    from webob.multidict import NestedMultiDict
    from pyramid_restful.utils import get_payload

    request = DummyRequest(NestedMultiDict({'test_param': '10'}))
    setattr(request, 'json_body', {'test_data': '11'})

    assert request.params.get('test_param') == '10'
    assert request.json_body.get('test_data') == '11'

    data = get_payload(request)

    assert len(data) == 2
    assert data['test_param'] == '10'
    assert data['test_data'] == '11'


def test_payload_parsing_for_overrides():
    from pyramid.testing import DummyRequest
    from webob.multidict import NestedMultiDict
    from pyramid_restful.utils import get_payload

    request = DummyRequest(NestedMultiDict({'test_param': '10'}))
    setattr(request, 'json_body', {'test_param': '11'})

    assert request.params.get('test_param') == '10'
    assert request.json_body.get('test_param') == '11'

    data = get_payload(request)

    assert len(data) == 1
    assert data['test_param'] == '11'
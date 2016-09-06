from pyramid.httpexceptions import HTTPBadRequest


def get_payload(request):
    """
    Extracts the request's payload information.
    This method will merge the URL parameter information
    and the JSON body of the request together to generate
    a dictionary of key<->value pairings.

    This method assumes that the JSON body being provided
    is also a key-value map, if it is not, then an HTTPBadRequest
    exception will be raised.

    :param request: <pyramid.request.Request>

    :return: <dict>
    """
    # always extract values from the URL
    payload = dict(request.params.mixed())

    # provide override capability from the JSON body
    try:
        json_data = request.json_body

    # no JSON body was found, pyramid raises an error
    # in this situation
    except StandardError:
        pass

    else:
        if not isinstance(json_data, dict):
            raise HTTPBadRequest('JSON body must be a key=value pairing')
        else:
            payload.update(json_data)

    return payload
from pyramid_restful import endpoint

_USER = None

def unexposed(request):
    return {}

@endpoint.get()
def login(request):
    """
    Testing method docs.

    {example}
    This is an example content.

        GET /api/v1/login
    {example}
    """
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
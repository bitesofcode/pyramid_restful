pyramid_restful
======================

The `pyramid_restful` project is an easy to use ReST service builder.

This project is a middleware plugin for the [Pyramid framework](http://www.pylonsproject.org),
a flexible Python HTTP server.

Installation
-----------------------

    pip install pyramid_restful

Documentation
-----------------------

### Getting Started

ReSTful interfaces work by defining endpoints based on HTTP method
verbage for different resources.  The pyramid_restful middle ware allows you to easily 
create these endpoints out of your modules using the `endpoint` decorator.

Let's assume that we have created a new website using the [pcreate](http://docs.pylonsproject.org/projects/pyramid/en/latest/narr/project.html)
command from Pyramid.  We would start with a site that looks like this:

    MyProject/
        myproject/
            static/
            templates/
            __init__.py
            tests.py
            views.py
    CHANGES.txt
    MANIFEST.in
    README.txt
    development.ini
    production.ini
    setup.py

We will use this as the basis for the rest of the documentation to make it easy to
follow along.

### Configuring API

Edit the `development.ini` and `production.ini` files to include these lines
underneath the `[app:main]` section:

```yaml
# restful configuration
restful.api.root = /api/v1
restful.api.version = 0.0.1
```

The first parameter will be the URL that pyramid will serve the API through.  The
second is the version that will be returned when the user hits that API endpoint.

### Including API

With those configuration values in place, you will also need to include the project
into your application.  You can do this either by including it with the `pyramid.includes`,
or within your global `Configurator` defined in the `myproject/__init__.py` file.

I tend to do this in the `__init__.py` file because this is an inclusion that will exist
for all environments, but either way works.

** Inclusion via Config **

Edit the `development.ini` and modify the `pyramid.includes` property to read:

```yaml
pyramid.includes =
    pyramid_debugtoolbar
    pyramid_restful
```

** Inclusion via Applicaiton **

Edit the `myproject/__init__.py` file to read add a `config.include('pyramid_restful')` line:

```python
...

def main(global_config, **settings):
    """ This function returns a Pyramid WSGI application.
    """
    config = Configurator(settings=settings)
    config.include('pyramid_chameleon')
    config.include('pyramid_restful')
    ...
```

### Testing the API

With these two pieces in place, you will now have the basics for your API server.  To test, you can
run your project and go to the `/api/v1` page:

```bash
$ pserve development.ini
Starting server in PID 12345.
serving on http://0.0.0.0:6543
```

If you go to [http://0.0.0.0:6543](http://0.0.0.0:6543) at this point, you will now see
automatically generated documentation for your API.  Included with the server, we also will
generate documentation based on the code that is exposed as endpoints here.  If you hit this
URL with an HTTP request, the documentation is returned.  If you request a JSON response, you will
see the version that was defined in the configuration files:

```bash
$ curl -i -H "Accept: application/json" http://localhost:643/api/v1
HTTP/1.1 200 OK
Content-Length: 26
Content-Type: application/json; charset=UTF-8
Date: Mon, 28 Mar 2016 23:15:06 GMT
Server: waitress

{
    "version": "0.0.1"
}
```

### Basic Endpoints

The API uses the [Pyramid traversal scheme](http://docs.pylonsproject.org/projects/pyramid/en/latest/narr/traversal.html)
for navigating resources.  That means the endpoints that you expose will all be
automatically added URLs _underneath_ the API root.

From here, let's start making defining the ReSTful API itself.  First, create a 
directory called `rest` within your `myproject` directory and add an `__init__.py` file:

    MyProject/
        myproject/
            static/
            templates/
            __init__.py
            rest.py
            tests.py
            views.py
    CHANGES.txt
    MANIFEST.in
    README.txt
    development.ini
    production.ini
    setup.py

Within the `rest.py` file, you will start defining your endpoints.  To do this, you
use the `endpoint` decorator from the `pyramid_restful` project.

As an example, you could do:

```python
from pyramid_restful import endpoint

_USER = None

@endpoint.post()
def login(request):
    username = request.params.get('username')
    _ = request.params.get('password')

    global _USER
    _USER = {'username': username}
    return _USER

@endpoint.get()
def whoami(request):
    return _USER

@endpoint.post()
def logout(request):
    global _USER
    _USER = None


def includeme(config):
    api = config.registry.rest_api

    # register various endpoints
    api.register(login)
    api.register(logout)
    api.register(whoami)
```

(Obviously you would never store a user this way, this is just an example
of running the server)

These endpoints are now registered underneath the api root (`/api/v1`) and can
be accessed via:

    GET     /api/v1/whoami
    POST    /api/v1/login
    POST    /api/v1/logout

The `endpoint` decorator allows you to define all the common HTTP verbs of a ReSTful interface:

    @endpoint.get()
    @endpoint.post()
    @endpoint.put()
    @endpoint.patch()
    @endpoint.delete()

Each of these decorators corresponds to a particular HTTP request method that can
be performed.  ReSTful interfaces use these methods to define resource states.  You could
also define this API like:

```python
from pyramid_restful import endpoint

_USER = None

@endpoint.get()
def login(request):
    return _USER

@login.post()
def set_login(request):
    username = request.params.get('username')
    _ = request.params.get('password')

    global _USER
    _USER = {'username': username}
    return _USER

@login.delete()
def unset_login(request):
    global _USER
    _USER = None


def includeme(config):
    api = config.registry.rest_api

    # register various endpoints
    api.register(login)
```

For this example, there is only 1 endpoint URL created, `/api/v1/login`, with 3 different
verbs associated with it.  Usage of the API routes are defined as:

    GET     /api/v1/login
    POST    /api/v1/login
    DELETE  /api/v1/login

This is technically the more "ReSTful" way to define your API.

### Subpaths

You can define additional sub-paths for the API by defining 
# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['drakaina',
 'drakaina.client',
 'drakaina.contrib',
 'drakaina.contrib.django',
 'drakaina.contrib.jwt',
 'drakaina.middleware',
 'drakaina.middleware.openapi',
 'drakaina.rpc_protocols']

package_data = \
{'': ['*']}

install_requires = \
['typing-extensions>=4.5.0,<5.0.0']

extras_require = \
{'docs': ['docstring-parser>=0.15,<0.16'],
 'jwt': ['pyjwt>=2.6.0,<3.0.0'],
 'msgpack': ['msgpack>=1.0.4,<2.0.0'],
 'orjson': ['orjson>=3.8.5,<4.0.0'],
 'tests': ['msgpack>=1.0.4,<2.0.0',
           'orjson>=3.8.5,<4.0.0',
           'ujson>=5.7.0,<6.0.0',
           'pyjwt>=2.6.0,<3.0.0',
           'docstring-parser>=0.15,<0.16'],
 'ujson': ['ujson>=5.7.0,<6.0.0']}

setup_kwargs = {
    'name': 'drakaina',
    'version': '0.7.0b0',
    'description': 'Module for simple RPC service implementation',
    'long_description': '# drakaina\n\n![Drakaina](content/drakaina.png "Drakaina"){width=200px height=205px}\n\n[![image](https://img.shields.io/pypi/v/drakaina.svg)](https://pypi.python.org/pypi/drakaina)\n[![image](https://img.shields.io/pypi/l/drakaina.svg)](https://pypi.python.org/pypi/drakaina)\n[![image](https://img.shields.io/pypi/pyversions/drakaina.svg)](https://pypi.python.org/pypi/drakaina)\n[![Ruff](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/charliermarsh/ruff/main/assets/badge/v1.json)](https://github.com/charliermarsh/ruff)\n[![Code style: black](https://img.shields.io/badge/code%20style-black-black.svg)](https://github.com/psf/black)\n[![libera manifesto](https://img.shields.io/badge/libera-manifesto-lightgrey.svg)](https://liberamanifesto.com)\n\n❗ WIP ❗\n\nFramework for simple RPC service implementation.\n\n\n## Quickstart\n\nDrakaina may be installed via `pip` and requires Python 3.7 or higher :\n\n```shell\npip install drakaina\n```\n\nA minimal Drakaina example is:\n\n```python\nfrom drakaina import remote_procedure\nfrom drakaina.wsgi import WSGIHandler\n\n@remote_procedure("hello")\ndef hello_method(name):\n    return f"Hello, {name}!"\n\n"""\n>>> from drakaina.rpc_protocols import JsonRPCv2\n>>> JsonRPCv2().handle({"jsonrpc": "2.0", "method": "hello", "params": ["🐍 Python"] "id": 1})\n{"jsonrpc": "2.0", "result": "Hello, 🐍 Python!", "id": 1}\n"""\n\n# Or define WSGI application\napp = WSGIHandler(route="/jrpc")\n\n```\n\n\n## Features\n\n- Serializers layer.\n  - `json`, `orjson`, `ujson` and `msgpack` serializers.\n- Generates schemas for documentation in OpenRPC format.\n- WSGI protocol implementation\n  - CORS middleware\n  - JWT Authorization middleware.\n  - Compatible with middlewares for others wsgi-frameworks,\n    like as [Werkzeug](https://palletsprojects.com/p/werkzeug/),\n    [Flask](https://palletsprojects.com/p/flask/)\n- `login_required` and `check_permissions` decorators.\n\n\n# Documentation\n\n\n## Installation\n\n```shell\npip install drakaina\n```\n\n\n## Middlewares\n\n\n### CORS\n\n\n### JWT\n\nDrakaina may be installed via `pip` and requires Python 3.7 or higher :\n\n```shell\npip install drakaina[jwt]\n```\n\nExample of using Drakaina:\n\n```python\nfrom functools import partial\nfrom drakaina import check_permissions\nfrom drakaina import ENV_IS_AUTHENTICATED\nfrom drakaina import ENV_USER_ID\nfrom drakaina import login_required\nfrom drakaina import match_any\nfrom drakaina import remote_procedure\nfrom drakaina.contrib.jwt.middleware import JWTAuthenticationMiddleware\nfrom drakaina.wsgi import WSGIHandler\n\nimport user_store\n\n\n@login_required\n@remote_procedure(provide_request=True)\ndef my_method(request):\n    assert request[ENV_IS_AUTHENTICATED]\n    return f"Hello Bro ✋! Your ID={request[ENV_USER_ID]}"\n\n\n@check_permissions(["user_read", "user:admin", "username:johndoe"], match_any)\n@remote_procedure\ndef my_method():\n    return "Hello Bro! ✋️"\n\n\ndef get_user(request, payload):\n    user_id = request[ENV_USER_ID] or payload["user_id"]\n    return user_store.get(id=user_id)\n\n\ndef get_jwt_scopes(request, payload):\n    # here `scp` is the key for the scopes value in the token payload\n    return payload.get("scp")\n\n\napp = WSGIHandler(\n    middlewares=[\n        partial(\n            JWTAuthenticationMiddleware,\n            secret_phrase="_secret_",\n            credentials_required=True,\n            auth_scheme="Bearer",\n            # token_getter=custom_implementation_get_token,\n            user_getter=get_user,\n            scopes_getter=get_jwt_scopes,\n            # revoke_checker=is_revoked,\n        )\n    ]\n)\n```\n\nDrakaina may be ran with any WSGI-compliant server,\nsuch as [Gunicorn](http://gunicorn.org).\n\n```shell\ngunicorn main:app\n```\n\nor ran with any ASGI-compliant server\n\n```shell\nuvicorn main:app2\n```\n\n\n### Using with Django\n\nCreate file `rpc_views.py` in your django application.\nDefine function and wrap it `remote_procedure` decorator:\n\n```python\nfrom drakaina import remote_procedure\n\n@remote_procedure\ndef my_method():\n    return "Hello, Django Bro! ✋"\n```\n\nAdd `RPCView` class to urlpatterns. The `as_view` method\nmust accept the `autodiscover` argument as the name of\nthe remote procedure files.\n\n```python\nfrom django.urls import path\nfrom drakaina.contrib.django.views import RPCView\n\nurlpatterns = [\n    ...,\n    path("api/", RPCView.as_view(autodiscover="rpc_views")),\n]\n```\n\n\n### JWT Authentication in your Django project\n\nWrap an instance of `RPCView` with the `JWTAuthenticationMiddleware`.\n\n```python\nfrom django.urls import path\nfrom drakaina.contrib.django import RPCView, JWTAuthenticationMiddleware\n\nurlpatterns = [\n    ...,\n    path("api/", JWTAuthenticationMiddleware(\n        RPCView.as_view(autodiscover="rpc_views")\n    )),\n]\n```\n\nDefine the parameters in the `settings.py` file.\n\n```python\n...\n\nDRAKAINA_JWT_SECRET_KEY = "__SECRET_KEY__"\n\n...\n```\n\n\n## License\n\nApache License 2.0\n\n## Artwork\n\n"[drakaina.png](content/drakaina.png)" by Korolko Anastasia is licensed under\n<a rel="license" href="http://creativecommons.org/licenses/by-sa/4.0/"><img alt="License Creative Commons" style="border-width:0" src="https://i.creativecommons.org/l/by-sa/4.0/80x15.png" /></a> ([CC BY-SA 4.0](http://creativecommons.org/licenses/by-sa/4.0/)).\n',
    'author': 'Aleksey Terentyev',
    'author_email': 'terentyev.a@pm.me',
    'maintainer': 'None',
    'maintainer_email': 'None',
    'url': 'https://gitlab.com/tau_lex/drakaina',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'extras_require': extras_require,
    'python_requires': '>=3.7,<4.0',
}


setup(**setup_kwargs)

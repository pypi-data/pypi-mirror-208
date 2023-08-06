# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['openapi_bridge']

package_data = \
{'': ['*']}

install_requires = \
['pydantic>=1.10.7,<2.0.0']

setup_kwargs = {
    'name': 'openapi-bridge',
    'version': '0.1.0',
    'description': '',
    'long_description': '# openapi-bridge\n\nOpenAPI endpoint decorator with pydantic integration.\n\nAllows for almost seamless integration of pydantic models with OpenAPI,\ngenerating YAML for the endpoint from type hints.\n\n\n## Using the `@endpoint` decorator\n\nExample:\n\n```python\n@endpoint("/foo/{foo_id}")\ndef foo(*, foo_id: int, debug: Optional[bool] = False) -> pydantic_models.Foo:\n   """\n       Foo summary.\n\n       Lengthy foo description.\n\n       @param foo_id The Foo ID in the database.\n       @param debug Set to True to include debug information.\n   """\n   result = _do_something(id, debug)\n   return pydantic_models.Foo(**result)\n```\n\nAs you can see from the example, the decorator takes a path (which may include\na path parameter, in this case `id`). You can also give it an HTTP method, a\npath prefix (e.g. to distinguish between internal and external API functions),\nand security directives.\n\nInformation about the endpoint is gathered from both the type annotations of\nthe decorated function and its docstring.\n\n(!) Every parameter (except the optional `user`) must be keyword-only, have a\ntype hint and a @param help text in the docstring. Un-annotated or undocumented\nparameters are considered to be a hard error and will raise an exception on\nstartup.\n\nNormally you can just return an instance of the annotated type, and the\ndecorator will handle it correctly, adding an HTTP status 200. If you need to\nreturn something else, e.g. some redirect or a 204 ("no content"), you can to\nreturn a `(raw_content, http_status)` tuple instead, e.g.:\n\n```python\nreturn None, 204\n```\n\nThe docstring of an endpoint contains its summary, description, the section the\ndocumentation is listed under, and parameter help, as well as (optionally) its\nresponse in various circumstances.\n\nThe summary is the first paragraph of the docstring; the description is taken\nto be any further paragraphs until the first @keyword.\n\nWe recognize the following keywords to designate parts of the documentation:\n - `@section <section name>`: endpoint is listed in this section.\n - `@param <param name> <help text>`: explanation of the given parameter.\n - `@example <param name> <example text>`: example values of the parameter.\n - `@response <http status> <JSON>`: allows for non-standard responses.\n\n\n## YAML Generation\n\nIf you\'re building a Connexion app, you can use the collected endpoints in your\n`create_app()` function:\n\n```python\ndef create_app():\n    # TODO: import all modules with @endpoints here!!\n    api_specs = {\n        "paths": openapi_bridge.PATHS["default"],\n        **openapi_bridge.get_pydantic_schemata(pydantic_models),\n    }\n    connexion_app.add_api(api_specs)\n```\n\n(!) You need to import all the modules with endpoints here in order to register\nthem. This is easy to forget! If you test a new endpoint and only ever get 404,\nyou might have forgotten to import that module ;-)\n',
    'author': 'Patrick Schemitz',
    'author_email': 'ps@solute.de',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/solute/openapi-bridge',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.9,<4.0',
}


setup(**setup_kwargs)

# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['spacs']

package_data = \
{'': ['*']}

install_requires = \
['aiohttp>=3.8.4,<4.0.0', 'pydantic>=1.10.7,<2.0.0']

setup_kwargs = {
    'name': 'spacs',
    'version': '0.0.9',
    'description': 'Simple Pydantic AIOHTTP Client Sessions',
    'long_description': '# SPACS: Simple Pydantic AIOHTTP Client Sessions\n\nA package to assist in managing and using long-lived AIOHTTP client sessions with simplicity. Built to handle Pydantic objects.\n\n## Features\n\n- Handles request params and bodies as either Pydantic objects or native Python dictionaries, converting items to JSON-safe format.\n- Abstracts away internals of managing the request/response objects, instead either returning parsed response content on success, or raising a specialized error object.\n- Automatically manages persistent connections to be shared over extended lifespan across application, cleaning up all open connections on teardown.\n- Utilizes modern Python type hinting.\n\n## Installation\n\nUsing poetry (preferred):\n\n```bash\npoetry add spacs\n```\n\nUsing pip:\n\n```bash\npip install spacs\n```\n\n## Basic Usage\nSPACS currently supports the HTTP methods GET, POST, PUT, and DELETE. All methods take the same, singular `SpacsRequest` argument. The following are some common patterns to be utilized when working with SPACS.\n### Request With Params\n```python\nimport asyncio\nfrom spacs import SpacsClient, SpacsRequest\n\nasync def example():\n    client = SpacsClient(base_url="https://httpbin.org")\n    request = SpacsRequest(path="/get", params={"foo": "bar"})\n    result = await client.get(request)\n    print(result)\n    await client.close()\n\nasyncio.new_event_loop().run_until_complete(example())\n```\n\n### Sending Pydantic objects via request body\n```python\nimport asyncio\nfrom spacs import SpacsClient, SpacsRequest\nfrom pydantic import BaseModel\n\nclass Person(BaseModel):\n    name: str\n    age: int\n\nasync def example():\n    client = SpacsClient(base_url="https://httpbin.org")\n    person = Person(name="James", age=25)\n    request = SpacsRequest(path="/post", body=person)\n    response = await client.post(request)\n    print(response)\n    await client.close()\n\nasyncio.new_event_loop().run_until_complete(example())\n```\n\n#### Tip: Response Model\nFor all examples here, if the API declares that response bodies will *only* contain json data representing a Pydantic object, the payload can be deserialized into an object by specifying a Pydantic class in the request. For example, using our above `Person` model:\n```python\nrequest = SpacsRequest(path="/post", body=person, response_model=Person)\nresponse = await client.post(request)\nassert isinstance(response, Person)\n```\n\n## Handling Errors\n### Manual Error Handling\n```python\nimport asyncio\nfrom spacs import SpacsClient, SpacsRequest, SpacsRequestError\n\nasync def example():\n    client = SpacsClient(base_url="https://httpbin.org")\n    request = SpacsRequest(path="/status/404")\n    try:\n        await client.get(request)\n    except SpacsRequestError as error:\n        print({"code": error.status, "reason": error.reason})\n    await client.close()\n\nasyncio.new_event_loop().run_until_complete(example())\n```\n\n### Injecting Error Handler\n```python\nimport asyncio\nfrom spacs import SpacsClient, SpacsRequest, SpacsRequestError\n\nasync def error_handler(error: SpacsRequestError) -> None:\n    print(f"It blew up: {error.reason}")\n    await error.client.close()\n\nasync def example():\n    client = SpacsClient(base_url="https://httpbin.org", error_handler=error_handler)\n    request = SpacsRequest(path="/status/504")\n    response = await client.get(request)\n    assert not client.is_open\n    assert response is None\n\nasyncio.new_event_loop().run_until_complete(example())\n```\n\n### Closing sessions\nIn the above examples, a `client.close()` call is made. This is to ensure that the underlying AIOHTTP session\nis properly cleaned up, and is a step that should always be performed on application teardown. Alternatively, the following can be used to close all open sessions without having to\ndirectly reference a client instance:\n```python\nawait SpacsClient.close_all()\n```\n> SPACS is not affiliated with httpbin.org.\n\n## Building\n\n```\npoetry build\n```\n',
    'author': 'rlebel12',
    'author_email': 'None',
    'maintainer': 'None',
    'maintainer_email': 'None',
    'url': 'https://github.com/rlebel12/spacs',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.11,<4.0',
}


setup(**setup_kwargs)

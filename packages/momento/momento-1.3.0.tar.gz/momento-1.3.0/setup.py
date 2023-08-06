# -*- coding: utf-8 -*-
from setuptools import setup

package_dir = \
{'': 'src'}

packages = \
['momento',
 'momento.auth',
 'momento.config',
 'momento.config.transport',
 'momento.errors',
 'momento.internal',
 'momento.internal._utilities',
 'momento.internal.aio',
 'momento.internal.synchronous',
 'momento.requests',
 'momento.responses',
 'momento.responses.control',
 'momento.responses.control.cache',
 'momento.responses.control.signing_key',
 'momento.responses.data',
 'momento.responses.data.dictionary',
 'momento.responses.data.list',
 'momento.responses.data.scalar',
 'momento.responses.data.set',
 'momento.responses.data.sorted_set',
 'momento.retry']

package_data = \
{'': ['*']}

install_requires = \
['grpcio>=1.50.0,<2.0.0',
 'momento-wire-types>=0.60,<0.61',
 'pyjwt>=2.4.0,<3.0.0']

setup_kwargs = {
    'name': 'momento',
    'version': '1.3.0',
    'description': 'SDK for Momento',
    'long_description': '<img src="https://docs.momentohq.com/img/logo.svg" alt="logo" width="400"/>\n\n[![project status](https://momentohq.github.io/standards-and-practices/badges/project-status-official.svg)](https://github.com/momentohq/standards-and-practices/blob/main/docs/momento-on-github.md)\n[![project stability](https://momentohq.github.io/standards-and-practices/badges/project-stability-stable.svg)](https://github.com/momentohq/standards-and-practices/blob/main/docs/momento-on-github.md) \n\n# Momento Python Client Library\n\n\nPython client SDK for Momento Serverless Cache: a fast, simple, pay-as-you-go caching solution without\nany of the operational overhead required by traditional caching solutions!\n\n\n\n## Getting Started :running:\n\n### Requirements\n\n- [Python 3.7](https://www.python.org/downloads/) or above is required\n- A Momento Auth Token is required, you can generate one using the [Momento CLI](https://github.com/momentohq/momento-cli)\n\n### Examples\n\nReady to dive right in? Just check out the [examples](https://github.com/momentohq/client-sdk-python/tree/main/examples) directory for complete, working examples of\nhow to use the SDK.\n\n### Installation\n\nThe [Momento SDK is available on PyPi](https://pypi.org/project/momento/). To install via pip:\n\n```bash\npip install momento\n```\n\n### Usage\n\nThe examples below require an environment variable named MOMENTO_AUTH_TOKEN which must\nbe set to a valid [Momento authentication token](https://docs.momentohq.com/docs/getting-started#obtain-an-auth-token).\n\nPython 3.10 introduced the `match` statement, which allows for [structural pattern matching on objects](https://peps.python.org/pep-0636/#adding-a-ui-matching-objects).\nIf you are running python 3.10 or greater, here is a quickstart you can use in your own project:\n\n```python\nfrom datetime import timedelta\n\nfrom momento import CacheClient, Configurations, CredentialProvider\nfrom momento.responses import CacheGet, CacheSet, CreateCache\n\nif __name__ == "__main__":\n    cache_name = "default-cache"\n    with CacheClient(\n        configuration=Configurations.Laptop.v1(),\n        credential_provider=CredentialProvider.from_environment_variable("MOMENTO_AUTH_TOKEN"),\n        default_ttl=timedelta(seconds=60),\n    ) as cache_client:\n        create_cache_response = cache_client.create_cache(cache_name)\n        match create_cache_response:\n            case CreateCache.CacheAlreadyExists():\n                print(f"Cache with name: {cache_name} already exists.")\n            case CreateCache.Error() as error:\n                raise error.inner_exception\n\n        print("Setting Key: foo to Value: FOO")\n        set_response = cache_client.set(cache_name, "foo", "FOO")\n        match set_response:\n            case CacheSet.Error() as error:\n                raise error.inner_exception\n\n        print("Getting Key: foo")\n        get_response = cache_client.get(cache_name, "foo")\n        match get_response:\n            case CacheGet.Hit() as hit:\n                print(f"Look up resulted in a hit: {hit}")\n                print(f"Looked up Value: {hit.value_string!r}")\n            case CacheGet.Miss():\n                print("Look up resulted in a: miss. This is unexpected.")\n            case CacheGet.Error() as error:\n                raise error.inner_exception\n\n```\n\nThe above code uses [structural pattern matching](https://peps.python.org/pep-0636/), a feature introduced in Python 3.10.\nUsing a Python version less than 3.10? No problem. Here is the same example compatible across all versions of Python:\n\n```python\nfrom datetime import timedelta\nfrom momento import CacheClient, Configurations, CredentialProvider\nfrom momento.responses import CacheGet, CacheSet, CreateCache\n\nif __name__ == "__main__":\n    cache_name = \'default-cache\'\n    with CacheClient(configuration=Configurations.Laptop.v1(),\n                     credential_provider=CredentialProvider.from_environment_variable(\'MOMENTO_AUTH_TOKEN\'),\n                     default_ttl=timedelta(seconds=60)\n                     ) as cache_client:\n        create_cache_response = cache_client.create_cache(cache_name)\n        if isinstance(create_cache_response, CreateCache.CacheAlreadyExists):\n            print(f"Cache with name: {cache_name} already exists.")\n        elif isinstance(create_cache_response, CreateCache.Error):\n            raise create_cache_response.inner_exception\n\n        print("Setting Key: foo to Value: FOO")\n        set_response = cache_client.set(cache_name, \'foo\', \'FOO\')\n        if isinstance(set_response, CacheSet.Error):\n            raise set_response.inner_exception\n\n        print("Getting Key: foo")\n        get_response = cache_client.get(cache_name, \'foo\')\n        if isinstance(get_response, CacheGet.Hit):\n            print(f"Look up resulted in a hit: {get_response.value_string}")\n            print(f"Looked up Value: {get_response.value_string}")\n        elif isinstance(get_response, CacheGet.Miss):\n            print("Look up resulted in a: miss. This is unexpected.")\n        elif isinstance(get_response, CacheGet.Error):\n            raise get_response.inner_exception\n```\n\n### Logging\n\nTo avoid cluttering DEBUG logging with per-method logs the Momento SDK adds a TRACE logging level. This will only happen\nif the TRACE level does not already exist.\n\nTo enable TRACE level logging you can call logging.basicConfig() before making any log statements:\n\n```python\nimport logging\n\nlogging.basicConfig(level=\'TRACE\')\n```\n\n### Error Handling\n\nComing Soon!\n\n### Tuning\n\nComing Soon!\n\n----------------------------------------------------------------------------------------\nFor more info, visit our website at [https://gomomento.com](https://gomomento.com)!\n',
    'author': 'Momento',
    'author_email': 'hello@momentohq.com',
    'maintainer': 'None',
    'maintainer_email': 'None',
    'url': 'https://gomomento.com',
    'package_dir': package_dir,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.7,<3.12',
}


setup(**setup_kwargs)

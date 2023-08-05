# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['pydio']

package_data = \
{'': ['*']}

setup_kwargs = {
    'name': 'pydio',
    'version': '0.4.1',
    'description': 'Simple and functional dependency injection toolkit for Python',
    'long_description': "![PyPI](https://img.shields.io/pypi/v/pydio)\n![PyPI - Python Version](https://img.shields.io/pypi/pyversions/pydio)\n![PyPI - License](https://img.shields.io/pypi/l/pydio)\n![PyPI - Downloads](https://img.shields.io/pypi/dm/pydio)\n[![codecov](https://codecov.io/gh/mwiatrzyk/pydio/branch/master/graph/badge.svg?token=Y6DJDSOR6M)](https://codecov.io/gh/mwiatrzyk/pydio)\n\n# PyDio\n\nSimple and functional dependency injection toolkit for Python.\n\n## About\n\nPyDio aims to be simple, yet still powerful, allowing you to feed\ndependencies inside your application in a flexible way. PyDio design is based\non simple assumption, that dependency injection can be achieved using simple\n**key-to-function** map, where **key** specifies **type of object** you want\nto inject and **function** is a **factory** function that creates\n**instances** of that type.\n\nIn PyDio, this is implemented using **providers** and **injectors**. You use\nproviders to configure your **key-to-function** mapping, and then you use\ninjectors to perform a **lookup** of a specific key and creation of the final\nobject.\n\nHere's a simple example:\n\n```python\nimport abc\n\nfrom pydio.api import Provider, Injector\n\nprovider = Provider()\n\n@provider.provides('greet')\ndef make_greet():\n    return 'Hello, world!'\n\ndef main():\n    injector = Injector(provider)\n    greet_message = injector.inject('greet')\n    print(greet_message)\n\nif __name__ == '__main__':\n    main()\n```\n\nNow you can save the snippet from above as ``example.py`` file and execute\nto see the output:\n\n```shell\n$ python example.py\nHello, world!\n```\n\n## Key features\n\n* Support for any hashable keys: class objects, strings, ints etc.\n* Support for any type of object factories: function, coroutine, generator,\n  asynchronous generator.\n* Automatic resource management via generator-based factories\n  (similar to pytest's fixtures)\n* Multiple environment support: testing, development, production etc.\n* Limiting created object's lifetime to user-defined scopes: global,\n  application, use-case etc.\n* No singletons used, so there is no global state...\n* ...but you still can create global injector on your own if you need it :-)\n\n## Installation\n\nYou can install PyDio using one of following methods:\n\n1) From PyPI (for stable releases):\n\n    ```shell\n    $ pip install PyDio\n    ```\n\n2) From test PyPI (for stable and development releases):\n\n    ```shell\n    $ pip install -i https://test.pypi.org/simple/ PyDio\n    ```\n\n3) Directly from source code repository (for all releases):\n\n    ```shell\n    $ pip install git+https://gitlab.com/zef1r/PyDio.git@[branch-or-tag]\n    ```\n\n## Documentation\n\nYou have two options available:\n\n1) Visit [PyDio's ReadTheDocs](https://pydio.readthedocs.io/en/latest/) site.\n\n2) Take a tour around [functional tests](https://github.com/mwiatrzyk/pydio/tree/master/tests/functional).\n\n## License\n\nThis project is released under the terms of the MIT license.\n\nSee [LICENSE.txt](https://github.com/mwiatrzyk/pydio/blob/master/LICENSE.txt) for more details.\n\n## Author\n\nMaciej Wiatrzyk <maciej.wiatrzyk@gmail.com>\n",
    'author': 'Maciej Wiatrzyk',
    'author_email': 'maciej.wiatrzyk@gmail.com',
    'maintainer': 'None',
    'maintainer_email': 'None',
    'url': 'https://github.com/mwiatrzyk/pydio',
    'packages': packages,
    'package_data': package_data,
    'python_requires': '>=3.7.2,<4',
}


setup(**setup_kwargs)

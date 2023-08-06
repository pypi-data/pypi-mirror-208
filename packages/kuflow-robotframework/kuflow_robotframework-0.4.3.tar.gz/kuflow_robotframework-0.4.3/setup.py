# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['KuFlow']

package_data = \
{'': ['*']}

install_requires = \
['kuflow-rest>=0.4.3,<0.5.0', 'robotframework>=5.0,<6.0']

extras_require = \
{':sys_platform != "win32"': ['python-magic>=0.4.27,<0.5.0'],
 ':sys_platform == "win32"': ['python-magic-bin>=0.4.14,<0.5.0']}

setup_kwargs = {
    'name': 'kuflow-robotframework',
    'version': '0.4.3',
    'description': 'KuFlow library for Robot Framework',
    'long_description': '[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](https://github.com/kuflow/kuflow-sdk-python/blob/master/LICENSE)\n[![Python](https://img.shields.io/pypi/pyversions/kuflow-robotframework.svg)](https://pypi.org/project/kuflow-robotframework)\n[![PyPI](https://img.shields.io/pypi/v/kuflow-robotframework.svg)](https://pypi.org/project/kuflow-robotframework)\n\n# KuFlow Robot Framework\n\nThis library provides keywords to interact with the KuFlow API from a Robot Framework Robot. Its purpose is to facilitate interaction from the robot logic (RPA). Its use helps to keep the manipulation of robot results by Workflow decoupled as much as possible.\n\nList of available keywords:\n\n#### Set Client Authentication\n\n> Configure the client authentication in order to execute keywords against Rest API\n\n#### Append Log Message\n\n> Add a log entry to the task\n\n#### Claim Task\n\n> Allow to claim a task\n\n#### Retrieve Process\n\n> Allow to get a process by ID\n\n#### Retrieve Task\n\n> Allow to get a task by ID\n\n#### Save Element Document\n\n> Save a element task of type document\n\n#### Delete Element Document\n\n> Allow to delete a specific document from an element of document type using its id.\n\n#### Save Element\n\n> Save a element task\n\n#### Delete Element\n\n> Allow to delete task element by specifying the item definition code.\n\n#### Convert To Principal Item\n\n> Given an Id of a Principal user, create an item that represents a reference to the Principal.\n\n#### Convert To Document Item From Uri\n\n> Given an Id of a Document or the URI reference of a Document, create an item that represents a reference to the Document elementand can be used.\n\n## Documentation\n\nMore detailed docs are available in the [documentation pages](https://docs.kuflow.com/developers/).\n\n## Contributing\n\nWe are happy to receive your help and comments, together we will dance a wonderful KuFlow. Please review our [contribution guide](CONTRIBUTING.md).\n\n## License\n\n[MIT License](https://github.com/kuflow/kuflow-sdk-python/blob/master/LICENSE)\n',
    'author': 'KuFlow S.L.',
    'author_email': 'kuflow@kuflow.com',
    'maintainer': 'None',
    'maintainer_email': 'None',
    'url': 'https://kuflow.com/',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'extras_require': extras_require,
    'python_requires': '>=3.8,<4.0',
}


setup(**setup_kwargs)

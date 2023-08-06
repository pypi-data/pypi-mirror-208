# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['kuflow_rest',
 'kuflow_rest._generated',
 'kuflow_rest._generated.aio',
 'kuflow_rest._generated.aio.operations',
 'kuflow_rest._generated.models',
 'kuflow_rest._generated.operations',
 'kuflow_rest.models',
 'kuflow_rest.operations']

package_data = \
{'': ['*']}

install_requires = \
['azure-core>=1.26.3,<2.0.0', 'isodate>=0.6.1,<0.7.0']

setup_kwargs = {
    'name': 'kuflow-rest',
    'version': '0.4.3',
    'description': 'Client for KuFlow Rest Api',
    'long_description': '[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](https://github.com/kuflow/kuflow-sdk-python/blob/master/LICENSE)\n[![Python](https://img.shields.io/pypi/pyversions/kuflow-rest.svg)](https://pypi.org/project/kuflow-rest)\n[![PyPI](https://img.shields.io/pypi/v/kuflow-rest.svg)](https://pypi.org/project/kuflow-rest)\n\n# KuFlow Rest\n\nThis is a client for the KuFlow API Rest that allows you to interact with our API in a comfortable way in the creation of your workers and tools.\n\n## Documentation\n\nMore detailed docs are available in the [documentation pages](https://docs.kuflow.com/developers/).\n\n## Contributing\n\nWe are happy to receive your help and comments, together we will dance a wonderful KuFlow. Please review our [contribution guide](CONTRIBUTING.md).\n\n## License\n\n[MIT License](https://github.com/kuflow/kuflow-sdk-python/blob/master/LICENSE)\n',
    'author': 'KuFlow S.L.',
    'author_email': 'kuflow@kuflow.com',
    'maintainer': 'None',
    'maintainer_email': 'None',
    'url': 'https://kuflow.com/',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.8,<4.0',
}


setup(**setup_kwargs)

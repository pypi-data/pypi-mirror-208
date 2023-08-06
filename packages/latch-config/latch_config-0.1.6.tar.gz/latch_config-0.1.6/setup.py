# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['latch_config']

package_data = \
{'': ['*']}

setup_kwargs = {
    'name': 'latch-config',
    'version': '0.1.6',
    'description': 'Shared config for latch python backend services',
    'long_description': '# python-config\n',
    'author': 'Max Smolin',
    'author_email': 'max@latch.bio',
    'maintainer': 'None',
    'maintainer_email': 'None',
    'url': 'None',
    'packages': packages,
    'package_data': package_data,
    'python_requires': '>=3.11,<4.0',
}


setup(**setup_kwargs)

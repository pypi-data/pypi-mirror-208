# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['cytotable']

package_data = \
{'': ['*']}

install_requires = \
['cloudpathlib[all]>=0.13.0,<0.14.0',
 'duckdb>=0.7.0,<0.8.0',
 'parsl>=2023.4.24,<2024.0.0',
 'pyarrow>=11.0.0,<12.0.0']

setup_kwargs = {
    'name': 'cytotable',
    'version': '0.0.1',
    'description': 'Transform data for processing image-based profiling readouts with Pycytominer.',
    'long_description': 'None',
    'author': 'Cytomining Community',
    'author_email': 'None',
    'maintainer': 'None',
    'maintainer_email': 'None',
    'url': 'None',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.8,<3.11',
}


setup(**setup_kwargs)

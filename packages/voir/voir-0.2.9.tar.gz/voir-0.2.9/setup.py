# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['voir', 'voir.instruments', 'voir.instruments.gpu']

package_data = \
{'': ['*']}

install_requires = \
['giving>=0.4.2,<0.5.0',
 'omegaconf>=2.3.0,<3.0.0',
 'ovld>=0.3.2,<0.4.0',
 'ptera>=1.4.1,<2.0.0',
 'pynvml>=11.5.0,<12.0.0',
 'rich>=13.3.2,<14.0.0']

entry_points = \
{'console_scripts': ['voir = voir.cli:main']}

setup_kwargs = {
    'name': 'voir',
    'version': '0.2.9',
    'description': 'Instrument, extend and visualize your programs',
    'long_description': 'None',
    'author': 'Olivier Breuleux',
    'author_email': 'breuleux@gmail.com',
    'maintainer': 'None',
    'maintainer_email': 'None',
    'url': 'None',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.7,<4.0',
}


setup(**setup_kwargs)

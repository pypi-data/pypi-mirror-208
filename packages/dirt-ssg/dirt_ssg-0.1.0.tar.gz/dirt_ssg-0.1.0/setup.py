# -*- coding: utf-8 -*-
from setuptools import setup

package_dir = \
{'': 'src'}

packages = \
['dirt']

package_data = \
{'': ['*']}

install_requires = \
['Markdown>=3.3.7,<4.0.0', 'toml>=0.10.2,<0.11.0', 'watchdog>=2.1.8,<3.0.0']

entry_points = \
{'console_scripts': ['dirt = dirt.main:main']}

setup_kwargs = {
    'name': 'dirt-ssg',
    'version': '0.1.0',
    'description': '',
    'long_description': 'None',
    'author': 'Loren Kohnfelder',
    'author_email': 'None',
    'maintainer': 'None',
    'maintainer_email': 'None',
    'url': 'None',
    'package_dir': package_dir,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.10,<4.0',
}


setup(**setup_kwargs)

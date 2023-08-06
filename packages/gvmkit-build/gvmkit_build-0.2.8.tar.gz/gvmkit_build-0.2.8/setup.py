# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['gvmkit_build']

package_data = \
{'': ['*']}

install_requires = \
['alive-progress>=1.5.1,<2.0.0',
 'argparse>=1.4.0,<2.0.0',
 'docker>=5.0,<6.0',
 'requests>=2.24.0,<3.0.0',
 'srvlookup>=2.0.0,<3.0.0',
 'termcolor==1.1.0',
 'typing>=3.7.4,<4.0.0',
 'typing_extensions>=3.7.4,<4.0.0']

entry_points = \
{'console_scripts': ['gvmkit-build = gvmkit_build:build']}

setup_kwargs = {
    'name': 'gvmkit-build',
    'version': '0.2.8',
    'description': '',
    'long_description': 'None',
    'author': 'Przemysław K. Rekucki',
    'author_email': 'prekucki@rcl.pl',
    'maintainer': 'None',
    'maintainer_email': 'None',
    'url': 'None',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.6,<4.0',
}


setup(**setup_kwargs)

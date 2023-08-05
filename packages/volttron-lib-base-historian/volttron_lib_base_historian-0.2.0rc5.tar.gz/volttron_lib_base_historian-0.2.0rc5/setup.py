# -*- coding: utf-8 -*-
from setuptools import setup

package_dir = \
{'': 'src',
 'historian': 'tests/historian',
 'historian.testing': 'tests/historian/testing'}

packages = \
['historian', 'historian.base', 'historian.testing']

package_data = \
{'': ['*']}

install_requires = \
['ply>=3.11,<4.0', 'volttron>=10.0.3a9,<11.0']

setup_kwargs = {
    'name': 'volttron-lib-base-historian',
    'version': '0.2.0rc5',
    'description': 'A base library with extension points for using with the VOLTTRON platform.',
    'long_description': '[![Eclipse VOLTTRON™](https://img.shields.io/badge/Eclips%20VOLTTRON--red.svg)](https://volttron.readthedocs.io/en/latest/)\n![Python 3.10](https://img.shields.io/badge/python-3.10-blue.svg)\n![Python 3.11](https://img.shields.io/badge/python-3.11-blue.svg)\n[![Run Pytests](https://github.com/eclipse-volttron/volttron-lib-base-historian/actions/workflows/run-tests.yml/badge.svg)](https://github.com/eclipse-volttron/volttron-lib-base-historian/actions/workflows/run-tests.yml)\n[![pypi version](https://img.shields.io/pypi/v/volttron-lib-base-historian.svg)](https://pypi.org/project/volttron-lib-base-historian/)\n\nVOLTTRON base historian framework that provide common functions such as caching, error handling, input validation etc. This historian cannot be used as agent as is. VOLTTRON historian agents can be created by subclassing the [BaseHistorian class](https://github.com/eclipse-volttron/volttron-lib-base-historian/blob/develop/src/historian/base/base_historian.py) in this library.\n\n## Requirements\n\n - Python >= 3.10\n\n## Installation\n\nThis library can be installed using ```pip install volttron-lib-base-historian```. However, this is not necessary. Any \nhistorian agent that uses this library will automatically install it as part of its installation. For example, \ninstalling [SQLiteHistorian](https://github.com/eclipse-volttron/volttron-sqlitehistorian) will automatically install \nvolttron-lib-base-historian into the same python environment\n\n## Development\n\nPlease see the following for contributing guidelines [contributing](https://github.com/eclipse-volttron/volttron-core/blob/develop/CONTRIBUTING.md).\n\nPlease see the following helpful guide about [developing modular VOLTTRON agents](https://github.com/eclipse-volttron/volttron-core/blob/develop/DEVELOPING_ON_MODULAR.md)\n\n# Disclaimer Notice\n\nThis material was prepared as an account of work sponsored by an agency of the\nUnited States Government.  Neither the United States Government nor the United\nStates Department of Energy, nor Battelle, nor any of their employees, nor any\njurisdiction or organization that has cooperated in the development of these\nmaterials, makes any warranty, express or implied, or assumes any legal\nliability or responsibility for the accuracy, completeness, or usefulness or any\ninformation, apparatus, product, software, or process disclosed, or represents\nthat its use would not infringe privately owned rights.\n\nReference herein to any specific commercial product, process, or service by\ntrade name, trademark, manufacturer, or otherwise does not necessarily\nconstitute or imply its endorsement, recommendation, or favoring by the United\nStates Government or any agency thereof, or Battelle Memorial Institute. The\nviews and opinions of authors expressed herein do not necessarily state or\nreflect those of the United States Government or any agency thereof.\n',
    'author': 'VOLTTRON Team',
    'author_email': 'volttron@pnnl.gov',
    'maintainer': 'None',
    'maintainer_email': 'None',
    'url': 'https://github.com/eclipse-volttron/volttron-lib-base-historian',
    'package_dir': package_dir,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.10,<4.0',
}


setup(**setup_kwargs)

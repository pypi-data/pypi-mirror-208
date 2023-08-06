# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['mpan', 'mpan.generation']

package_data = \
{'': ['*']}

install_requires = \
['coverage[toml]>=6.2,<7.0']

extras_require = \
{'faker': ['Faker>=10.0.0,<11.0.0'], 'mimesis': ['mimesis>=5.1.0,<6.0.0']}

setup_kwargs = {
    'name': 'mpan',
    'version': '2.1.0',
    'description': "A parsing library for the UK's MPAN energy standard",
    'long_description': "[![Limejump logo](https://raw.githubusercontent.com/limejump/mpan/master/docs/logo.png)](https://limejump.com/)\n\n\n# mpan\n\n[![PyPI](https://img.shields.io/pypi/pyversions/mpan)](https://pypi.org/project/mpan)\n[![PyPI](https://img.shields.io/pypi/wheel/mpan)](https://pypi.org/project/mpan)\n[![License](https://img.shields.io/pypi/l/mpan)](https://mit-license.org/)\n[![Black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/ambv/black)\n![100% Coverage](https://img.shields.io/badge/coverage-100%25-4ec820.svg)\n\nA library to help you parse the UK energy industry's MPAN number format.\n\n## Links\n\n* [Official documentation](https://limejump.github.io/mpan/)\n* [Wikipedia article on the MPAN standard](https://en.wikipedia.org/wiki/Meter_Point_Administration_Number)\n",
    'author': 'Limejump Developers',
    'author_email': 'opensource@limejump.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/limejump/mpan',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'extras_require': extras_require,
    'python_requires': '>=3.8,<4.0',
}


setup(**setup_kwargs)

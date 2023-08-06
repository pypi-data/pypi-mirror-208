# -*- coding: utf-8 -*-
from setuptools import setup

package_dir = \
{'': 'src'}

packages = \
['ib110hw_testing', 'ib110hw_testing.testing', 'ib110hw_testing.transformation']

package_data = \
{'': ['*']}

install_requires = \
['exrex', 'hypothesis', 'ib110hw']

setup_kwargs = {
    'name': 'ib110hw-testing',
    'version': '0.1.10',
    'description': 'Package used for testing homework assignments in the IB110 course at FI MUNI.',
    'long_description': 'This library was created for the course **IB110 - Introduction to Informatics** at [MUNI FI](https://www.fi.muni.cz/).\n\n# Setup\nThe library can be installed using `pip` like so:\n```pip install ib110hw_testing```\n\nI recommend using venv to install the library as it has some dependencies.\n\n# Modules\n## Testing\nThe module `testing` contains some predefined strategies which can be used with the `hypothesis` library. \n\n## Transformation\nThe module `transformation` contains some implementations of some algorithms which can be used to transform automata. \n',
    'author': 'Martin Pilát',
    'author_email': '8pilatmartin8@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'package_dir': package_dir,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.6.8,<4.0.0',
}


setup(**setup_kwargs)

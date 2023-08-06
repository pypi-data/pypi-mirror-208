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
    'version': '0.1.11',
    'description': 'Package used for testing homework assignments in the IB110 course at FI MUNI.',
    'long_description': 'This library was created for the course **IB110 - Introduction to Informatics** at [MUNI FI](https://www.fi.muni.cz/). It builds on top of the [ib110hw](https://pypi.org/project/ib110hw/) and the [hypothesis](https://pypi.org/project/hypothesis/) libraries.\n\n# Setup\n\nPython version required for this library is **>=3.6**. It can be installed using `pip` like so:\n```pip install ib110hw_testing```\n\nUsing venv to install the library is recommended as it has some dependencies (`ib110hw`, `exrex`, `hypothesis`).\n\n# Modules\n\n## Testing\n\nThe module `testing` contains some predefined strategies which can be used with the `hypothesis` library.\n\n### Example Use-case\n\nBelow code shows a simple example of strategies used with tests.\n\n```python\nfrom hypothesis import given\nfrom ib110hw.automaton.dfa import DFA\nfrom ib110hw_testing.testing.strategies import dfas, strings_from_regex\nfrom typing import Set\n\n@given(\n    dfas(alphabet={"a", "b", "c"}),\n    strings_from_regex(regex="[abc]*")\n)\ndef test(dfa: DFA, strings: Set[str])\n    ...\n```\n\n## Transformation\n\nThe module `transformation` contains implementations of some algorithms which can be used to transform automata.\n\n### Example Use-case\n\nBelow code shows a simple example of automata comparison.\n\n```python\nfrom ib110hw.automaton.dfa import DFA\nfrom ib110hw.automaton.nfa import NFA\nfrom ib110hw_testing.transformation.transformation import compare_automata\n\nnfa: NFA = NFA(...) # an arbitrary NFA\ndfa: DFA = DFA(...) # an arbitrary DFA\n\ncompare_automata(nfa, dfa) # returns True/False\n```\n',
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

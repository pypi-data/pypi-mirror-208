# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['woke',
 'woke.analysis',
 'woke.analysis.detectors',
 'woke.analysis.detectors.axelar',
 'woke.ast',
 'woke.ast.ir',
 'woke.ast.ir.declaration',
 'woke.ast.ir.expression',
 'woke.ast.ir.meta',
 'woke.ast.ir.statement',
 'woke.ast.ir.type_name',
 'woke.ast.ir.utils',
 'woke.ast.ir.yul',
 'woke.cli',
 'woke.compiler',
 'woke.compiler.solc_frontend',
 'woke.config',
 'woke.contracts',
 'woke.contracts.woke',
 'woke.core',
 'woke.deployment',
 'woke.development',
 'woke.development.json_rpc',
 'woke.lsp',
 'woke.lsp.commands',
 'woke.lsp.features',
 'woke.lsp.utils',
 'woke.regex_parser',
 'woke.svm',
 'woke.templates.scripts',
 'woke.templates.tests',
 'woke.testing',
 'woke.testing.fuzzing',
 'woke.utils']

package_data = \
{'': ['*']}

install_requires = \
['abch_tree_sitter>=1.1.1,<2.0.0',
 'abch_tree_sitter_solidity>=1.2.0,<2.0.0',
 'aiofiles>=0.8,<0.9',
 'aiohttp>=3.8,<4.0',
 'click>=8,<9',
 'eth-abi>=4.0.0b2,<5.0.0',
 'eth-account>=0.8,<0.9',
 'eth-hash[pycryptodome]>=0.5.1,<0.6.0',
 'eth-utils>=2.1,<3.0',
 'graphviz>=0.19,<0.20',
 'intervaltree>=3.1,<4.0',
 'ipdb>=0.13.9,<0.14.0',
 'networkx>=2.5,<3.0',
 'parsimonious>=0.9,<0.10',
 'pathvalidate>=2.5,<3.0',
 'pydantic>=1.9.1,<2.0.0',
 'pytest>=7,<8',
 'rich-click>=1.6,<2.0',
 'rich>=13.3.2,<14.0.0',
 'tblib>=1.7,<2.0',
 'tomli>=2,<3',
 'typing-extensions>=4,<5',
 'watchdog>=2.2.0,<2.3.0',
 'websocket-client>=1.4,<2.0']

extras_require = \
{':sys_platform == "win32"': ['pywin32>=302'],
 'dev': ['black>=22,<23',
         'mkdocs-material>=9,<10',
         'mkdocstrings[python]>=0.19,<0.20',
         'pymdown-extensions>=9,<10',
         'pygments>=2,<3',
         'isort>=5,<6',
         'pillow>=9,<10',
         'cairosvg>=2.7,<3.0'],
 'tests': ['pytest-asyncio>=0.17,<0.18', 'GitPython>=3.1.20,<4.0.0']}

entry_points = \
{'console_scripts': ['woke = woke.cli.__main__:main',
                     'woke-solc = woke.cli.__main__:woke_solc']}

setup_kwargs = {
    'name': 'woke',
    'version': '3.4.0',
    'description': 'Woke is a Python-based development and testing framework for Solidity.',
    'long_description': '# Woke\n\nWoke is a Python-based development and testing framework for Solidity.\n\nFeatures:\n\n- **Testing framework** - a testing framework for Solidity smart contracts with Python-native equivalents of Solidity types and blazing fast execution.\n\n- **Fuzzer** - a property-based fuzzer for Solidity smart contracts that allows testers to write their fuzz tests in Python.\n\n- **Vulnerability detectors**\n\n- **LSP server**\n\n## Dependencies\n\n- [Python](https://www.python.org/downloads/release/python-3910/) (version 3.7 or higher)\n\n> :warning: Python 3.11 is experimentally supported.\n\n## Installation\n\nvia `pip`\n\n```shell\npip3 install woke\n```\n\n## Documentation & Contribution\n\nWoke documentation can be found [here](https://ackeeblockchain.com/woke/docs/latest).\n\nThere you can also find a section on [contributing](https://ackeeblockchain.com/woke/docs/latest/contributing/).\n\n## Features\n\n### Testing framework\n\nSee [examples](examples) and [documentation](https://ackeeblockchain.com/woke/docs/latest/testing-framework/overview) for more information.\n\nWriting tests is as simple as:\n\n```python\nfrom woke.testing import *\nfrom pytypes.contracts.Counter import Counter\n\n@default_chain.connect()\ndef test_counter():\n    default_chain.set_default_accounts(default_chain.accounts[0])\n\n    counter = Counter.deploy()\n    assert counter.count() == 0\n\n    counter.increment()\n    assert counter.count() == 1\n```\n\n### Fuzzer\n\nFuzzer builds on top of the testing framework and allows efficient fuzz testing of Solidity smart contracts.\n\n```python\nfrom woke.testing import *\nfrom woke.testing.fuzzing import *\nfrom pytypes.contracts.Counter import Counter\n\nclass CounterTest(FuzzTest):\n    def pre_sequence(self) -> None:\n        self.counter = Counter.deploy()\n        self.count = 0\n\n    @flow()\n    def increment(self) -> None:\n        self.counter.increment()\n        self.count += 1\n\n    @flow()\n    def decrement(self) -> None:\n        with may_revert(Panic(PanicCodeEnum.UNDERFLOW_OVERFLOW)) as e:\n            self.counter.decrement()\n\n        if e.value is not None:\n            assert self.count == 0\n        else:\n            self.count -= 1\n\n    @invariant(period=10)\n    def count(self) -> None:\n        assert self.counter.count() == self.count\n\n@default_chain.connect()\ndef test_counter():\n    default_chain.set_default_accounts(default_chain.accounts[0])\n    CounterTest().run(sequences_count=30, flows_count=100)\n```\n\n### Vulnerability detectors\n\nVulnerability detectors can be run using:\n```shell\nwoke detect\n```\n\n### LSP server\n\nWoke implements an [LSP](https://microsoft.github.io/language-server-protocol/) server for Solidity. The only currently supported communication channel is TCP.\n\nWoke LSP server can be run using:\n\n```shell\nwoke lsp\n```\n\nOr with an optional --port argument:\n\n```shell\nwoke lsp --port 1234\n```\n\nAll LSP server features can be found in the [documentation](https://ackeeblockchain.com/woke/docs/latest/language-server/).\n\n## License\n\nThis project is licensed under the [ISC license](https://github.com/Ackee-Blockchain/woke/blob/main/LICENSE).\n\n## Partners\n\nRockawayX             |  Coinbase\n:-------------------------:|:-------------------------:\n[![](https://github.com/Ackee-Blockchain/woke/blob/main/images/rockawayx.jpg?raw=true)](https://rockawayx.com/)  |  [![](https://github.com/Ackee-Blockchain/woke/blob/main/images/coinbase.png?raw=true)](https://www.coinbase.com/)\n\n\n\n\n\n\n',
    'author': 'Ackee Blockchain',
    'author_email': 'None',
    'maintainer': 'None',
    'maintainer_email': 'None',
    'url': 'https://ackeeblockchain.com',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'extras_require': extras_require,
    'entry_points': entry_points,
    'python_requires': '>=3.7.9,<4.0.0',
}


setup(**setup_kwargs)

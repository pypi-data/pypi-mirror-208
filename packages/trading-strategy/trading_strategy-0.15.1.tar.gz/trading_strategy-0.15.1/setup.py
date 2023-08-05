# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['tradingstrategy',
 'tradingstrategy.analysis',
 'tradingstrategy.charting',
 'tradingstrategy.direct_feed',
 'tradingstrategy.environment',
 'tradingstrategy.frameworks',
 'tradingstrategy.testing',
 'tradingstrategy.transport',
 'tradingstrategy.utils']

package_data = \
{'': ['*'],
 'tradingstrategy': ['chains/*',
                     'chains/.ci/*',
                     'chains/.github/*',
                     'chains/.github/ISSUE_TEMPLATE/*',
                     'chains/.github/workflows/*',
                     'chains/_data/chains/*',
                     'chains/_data/chains/deprecated/*',
                     'chains/_data/icons/*',
                     'chains/gradle/wrapper/*',
                     'chains/src/main/kotlin/org/ethereum/lists/chains/*',
                     'chains/src/main/kotlin/org/ethereum/lists/chains/model/*',
                     'chains/src/test/kotlin/org/ethereum/lists/chains/*',
                     'chains/src/test/resources/test_chains/invalid/*',
                     'chains/src/test/resources/test_chains/invalid/explorerinvalidurl/*',
                     'chains/src/test/resources/test_chains/invalid/explorermissingurl/*',
                     'chains/src/test/resources/test_chains/invalid/explorernoname/*',
                     'chains/src/test/resources/test_chains/invalid/explorersnotarray/*',
                     'chains/src/test/resources/test_chains/invalid/sameshortname/*',
                     'chains/src/test/resources/test_chains/invalid/withparentchaindoesnotexist/*',
                     'chains/src/test/resources/test_chains/invalid/withparentextrabridgeelementnoobject/*',
                     'chains/src/test/resources/test_chains/invalid/withparentextrabridgesfield/*',
                     'chains/src/test/resources/test_chains/invalid/withparentextrabridgesnoarray/*',
                     'chains/src/test/resources/test_chains/invalid/withparentextrafield/*',
                     'chains/src/test/resources/test_chains/invalid/withparentinvalidtype/*',
                     'chains/src/test/resources/test_chains/invalid/withparentnobject/*',
                     'chains/src/test/resources/test_chains/invalid/wrongexplorerstandard/*',
                     'chains/src/test/resources/test_chains/valid/*',
                     'chains/src/test/resources/test_chains/valid/withexplorer/*',
                     'chains/src/test/resources/test_chains/valid/withparent/*',
                     'chains/src/test/resources/test_chains/valid/withparentbridge/*']}

install_requires = \
['dataclasses-json>=0.5.4,<0.6.0',
 'jsonlines>=3.1.0,<4.0.0',
 'pandas>=1.3.5,<2.0.0',
 'plotly>=5.1.0,<6.0.0',
 'pyarrow==10.0.1',
 'requests>=2.28.1,<3.0.0',
 'tqdm-loggable>=0.1.2,<0.2.0',
 'tqdm>=4.61.2,<5.0.0']

extras_require = \
{':extra == "direct-feed"': ['web3-ethereum-defi==0.18.1'],
 'backtrader': ['trading-strategy-backtrader>=0.1,<0.2'],
 'direct-feed': ['typer>=0.7.0,<0.8.0', 'dash>=2.7.1,<3.0.0'],
 'qstrader': ['trading-strategy-qstrader>=0.5.0,<0.6.0', 'scipy>=1.6.1,<2.0.0']}

setup_kwargs = {
    'name': 'trading-strategy',
    'version': '0.15.1',
    'description': 'DEX and cryptocurrency trading data for Python - OHCLV, Uniswap, others',
    'long_description': '[![PyPI version](https://badge.fury.io/py/trading-strategy.svg)](https://badge.fury.io/py/trading-strategy)\n\n[![CI Status](https://github.com/tradingstrategy-ai/trading-strategy/actions/workflows/python-app.yml/badge.svg)](https://github.com/tradingstrategy-ai/trading-strategy/actions/workflows/python-app.yml)\n\n[![pip installation works](https://github.com/tradingstrategy-ai/trading-strategy/actions/workflows/pip-install.yml/badge.svg)](https://github.com/tradingstrategy-ai/trading-strategy/actions/workflows/pip-install.yml)\n\n<a href="https://tradingstrategy.ai">\n  <img src="https://raw.githubusercontent.com/tradingstrategy-ai/trading-strategy/master/logo.svg" width="384">\n</a>\n\n# Trading Strategy framework for Python\n\nTrading Strategy framework is a Python framework for algorithmic trading on decentralised exchanges. \nIt is using [backtesting data](https://tradingstrategy.ai/trading-view/backtesting) and [real-time price feeds](https://tradingstrategy.ai/trading-view)\nfrom [Trading Strategy Protocol](https://tradingstrategy.ai/). \n\n# Use cases\n\n* Analyse cryptocurrency investment opportunities on [decentralised exchanges (DEXes)](https://tradingstrategy.ai/trading-view/exchanges)\n\n* Creating trading algorithms and trading bots that trade on DEXes\n\n* Deploy trading strategies as on-chain smart contracts where users can invest and withdraw with their wallets\n\n# Features\n\n* Supports multiple blockchains like [Ethereum mainnet](https://tradingstrategy.ai/trading-view/ethereum), \n  [Binance Smart Chain](https://tradingstrategy.ai/trading-view/binance) and \n  [Polygon](https://tradingstrategy.ai/trading-view/polygon)\n\n* Access trading data from on-chain decentralised exchanges like\n  [SushiSwap](https://tradingstrategy.ai/trading-view/ethereum/sushi), [QuickSwap](https://tradingstrategy.ai/trading-view/polygon/quickswap) and [PancakeSwap](https://tradingstrategy.ai/trading-view/binance/pancakeswap-v2)\n\n* Integration with Jupyter Notebook for easy manipulation of data.\n  See [example notebooks](https://tradingstrategy.ai/docs/programming/code-examples/index.html).\n\n* Write [algorithmic trading strategies](https://tradingstrategy.ai/docs/programming/strategy-examples/index.html) for  decentralised exchange \n\n# Getting started \n\nSee [the Getting Started tutorial](https://tradingstrategy.ai/docs/programming/code-examples/getting-started.html) and the rest of the [Trading Strategy documentation](https://tradingstrategy.ai/docs/).\n\n# Prerequisites\n\n* Python 3.10\n\n# Installing the package\n\n**Note**: Unless you are an experienced Python developer, [try the Binder cloud hosted Jupyter notebook examples first](https://tradingstrategy.ai/docs/programming/code-examples/index.html).\n\nYou can install this package with \n\n[Poetry](https://python-poetry.org/) as a dependency:\n\n```shell\npoetry add trading-strategy -E direct-feed\n```\n\nPoetry, local development:\n\n```shell\npoetry install -E direct-feed\n```\n\nPip:\n\n```shell\npip install "trading-strategy[direct-feed]" \n```\n\n# Documentation\n\n- [Read Trading Strategy documentation](https://tradingstrategy.ai/docs/).\n- [Documentation Github repository](https://github.com/tradingstrategy-ai/docs).\n\nCommunity\n---------\n\n* [Trading Strategy website](https://tradingstrategy.ai)\n\n* [Blog](https://tradingstrategy.ai/blog)\n\n* [Twitter](https://twitter.com/TradingProtocol)\n\n* [Discord](https://tradingstrategy.ai/community#discord) \n\n* [Telegram channel](https://t.me/trading_protocol)\n\n* [Changelog and version history](https://github.com/tradingstrategy-ai/trading-strategy/blob/master/CHANGELOG.md)\n\n[Read more documentation how to develop this package](https://tradingstrategy.ai/docs/programming/development.html).\n\n# License\n\nGNU AGPL 3.0. \n',
    'author': 'Mikko Ohtamaa',
    'author_email': 'mikko@tradingstrategy.ai',
    'maintainer': 'None',
    'maintainer_email': 'None',
    'url': 'https://tradingstrategy.ai',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'extras_require': extras_require,
    'python_requires': '>=3.10,<3.11',
}


setup(**setup_kwargs)

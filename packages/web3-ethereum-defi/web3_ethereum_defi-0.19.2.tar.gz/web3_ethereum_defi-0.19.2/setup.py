# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['eth_defi',
 'eth_defi.aave_v3',
 'eth_defi.chainlink',
 'eth_defi.enzyme',
 'eth_defi.event_reader',
 'eth_defi.price_oracle',
 'eth_defi.research',
 'eth_defi.uniswap_v2',
 'eth_defi.uniswap_v3']

package_data = \
{'': ['*'],
 'eth_defi': ['abi/*',
              'abi/aave_v3/*',
              'abi/dhedge/*',
              'abi/enzyme/*',
              'abi/sushi/*',
              'abi/uniswap_v3/*']}

install_requires = \
['eth-bloom>=2.0.0,<3.0.0',
 'evm-trace>=0.1.0a17,<0.2.0',
 'futureproof>=0.3.1,<0.4.0',
 'psutil>=5.9.0,<6.0.0',
 'setuptools>=65.6.3,<66.0.0',
 'tqdm-loggable>=0.1.3,<0.2.0',
 'ujson==5.7.0',
 'web3[tester]==6.0.0']

extras_require = \
{'data': ['tqdm>=4.64.0,<5.0.0',
          'pandas>=1.4.2,<2.0.0',
          'gql[requests]>=3.3.0,<4.0.0',
          'jupyter>=1.0.0,<2.0.0',
          'matplotlib>=3.5.2,<4.0.0',
          'plotly>=5.8.2,<6.0.0',
          'pyarrow>=10.0.1,<11.0.0'],
 'docs': ['Sphinx>=4.5.0,<5.0.0',
          'sphinx-rtd-theme>=1.0.0,<2.0.0',
          'sphinx-sitemap>=2.2.0,<3.0.0',
          'sphinx-autodoc-typehints>=1.16.0,<2.0.0',
          'nbsphinx>=0.8.9,<0.9.0',
          'furo>=2022.6.4.1,<2023.0.0.0']}

setup_kwargs = {
    'name': 'web3-ethereum-defi',
    'version': '0.19.2',
    'description': 'Python library for Uniswap, Aave, ChainLink, Enzyme and other protocols on BNB Chain, Polygon, Ethereum and other blockchains',
    'long_description': '[![PyPI version](https://badge.fury.io/py/web3-ethereum-defi.svg)](https://badge.fury.io/py/web3-ethereum-defi)\n\n[![Automated test suite](https://github.com/tradingstrategy-ai/web3-ethereum-defi/actions/workflows/test.yml/badge.svg)](https://github.com/tradingstrategy-ai/web3-ethereum-defi/actions/workflows/test.yml)\n\n[![Documentation Status](https://readthedocs.org/projects/web3-ethereum-defi/badge/?version=latest)](https://web3-ethereum-defi.readthedocs.io/)\n\n# Web3-Ethereum-Defi\n\nThis project contains high level Python API for smart contracts, \nDeFi trading, wallet management, automated test suites and backend integrations on EVM based blockchains.\nSupported blockchains include Ethereum, BNB Chain, Polygon, Avalanche C-chain, Arbitrum, others.\n \n* [Use Cases](#use-cases)\n* [Features](#features)\n* [Prerequisites](#prerequisites)\n* [Install](#install)\n* [Code examples](#code-examples)\n   * [Deploy and transfer ERC-20 token between wallets](#deploy-and-transfer-erc-20-token-between-wallets)\n   * [Uniswap v2 trade example](#uniswap-v2-trade-example)\n   * [Uniswap v2 price estimation example](#uniswap-v2-price-estimation-example)\n* [How to use the library in your Python project](#how-to-use-the-library-in-your-python-project)\n* [Documentation](#documentation)\n* [Development and contributing](#development-and-contributing)\n* [Version history](#version-history)\n* [Support](#support)\n* [Social media](#social-media)\n* [Notes](#notes)\n* [History](#history)\n* [License](#license)\n\n![Pepe chooses Web3-Ethereum-DeFi and Python](https://raw.githubusercontent.com/tradingstrategy-ai/web3-ethereum-defi/master/docs/source/_static/pepe.jpg)\n\n**Pepe chooses web3-ethereum-defi and Python**.\n\n# Use Cases\n\n* Web3 development\n* DeFi trading\n* Market data services\n* On-chain data research\n* Ethereum integration: token payments, hot wallets, monitors and such \n\n# Features\n\nFeatures include \n\n* [Made for 99% developers](https://future.a16z.com/software-development-building-for-99-developers/)\n* [High-quality API documentation](https://web3-ethereum-defi.readthedocs.io/)\n* [Fully type hinted](https://web3-ethereum-defi.readthedocs.io/) for good developer experience\n* [Parallel transaction execution](https://web3-ethereum-defi.readthedocs.io/en/latest/_autosummary/eth_defi.txmonitor.html)\n* [Mainnet forking with Anvil](https://web3-ethereum-defi.readthedocs.io/api/_autosummary/eth_defi.anvil.html#module-eth_defi.anvil)\n* [Solidity stack traces](https://web3-ethereum-defi.readthedocs.io/api/_autosummary/eth_defi.trace.html)\n* [Trading](https://web3-ethereum-defi.readthedocs.io/api/index.html)\n* [Loans](https://web3-ethereum-defi.readthedocs.io/api/index.html)\n* [ERC-20 token issuance and manipulation](https://web3-ethereum-defi.readthedocs.io/en/latest/_autosummary/eth_defi.token.html#module-eth_defi.token)\n\nWeb3-Ethereum-Defi supports \n\n* Uniswap (both v2 and v3)\n* Sushi\n* Aave \n* Enzyme Protocol\n* dHEDGE Protocol\n* More integrations to come\n* Built-in integration for over 600 smart contracts with precompiled Solidity ABI files \n\n[Read the full API documentation](https://web3-ethereum-defi.readthedocs.io/)).\nFor code examples please see below.\n\n# Prerequisites\n\nTo use this package you need to\n\n* Have Python 3.10 or higher\n* [Be proficient in Python programming](https://wiki.python.org/moin/BeginnersGuide)\n* [Understand of Web3.py library](https://web3py.readthedocs.io/en/stable/) \n* [Understand Pytest basics](https://docs.pytest.org/)\n\n# Install\n\nWith `pip`:\n\n```shell\npip install "web3-ethereum-defi[data]"\n```\n\nWith `poetry`:\n\n```shell\n# Poetry version\npoetry add -E data web3-ethereum-defi\n```\n\nWith `poetry` - master Git branch: \n\n```shell\ngit clone git@github.com:tradingstrategy-ai/web3-ethereum-defi.git\ncd web3-ethereum-defi\npoetry shell\npoetry install -E data -E docs \n```\n\n\n\n# Code examples\n\nFor more code examples, see [the tutorials section in the documentation](https://web3-ethereum-defi.readthedocs.io/tutorials/index.html).  \n\n## Deploy and transfer ERC-20 token between wallets\n\nTo use the package to deploy a simple ERC-20 token in [pytest](https://docs.pytest.org/) testing:\n\n```python\nimport pytest\nfrom web3 import Web3, EthereumTesterProvider\n\nfrom eth_defi.token import create_token\n\n\n@pytest.fixture\ndef tester_provider():\n  return EthereumTesterProvider()\n\n\n@pytest.fixture\ndef eth_tester(tester_provider):\n  return tester_provider.ethereum_tester\n\n\n@pytest.fixture\ndef web3(tester_provider):\n  return Web3(tester_provider)\n\n\n@pytest.fixture()\ndef deployer(web3) -> str:\n  """Deploy account."""\n  return web3.eth.accounts[0]\n\n\n@pytest.fixture()\ndef user_1(web3) -> str:\n  """User account."""\n  return web3.eth.accounts[1]\n\n\n@pytest.fixture()\ndef user_2(web3) -> str:\n  """User account."""\n  return web3.eth.accounts[2]\n\n\ndef test_deploy_token(web3: Web3, deployer: str):\n  """Deploy mock ERC-20."""\n  token = create_token(web3, deployer, "Hentai books token", "HENTAI", 100_000 * 10 ** 18)\n  assert token.functions.name().call() == "Hentai books token"\n  assert token.functions.symbol().call() == "HENTAI"\n  assert token.functions.totalSupply().call() == 100_000 * 10 ** 18\n  assert token.functions.decimals().call() == 18\n\n\ndef test_tranfer_tokens_between_users(web3: Web3, deployer: str, fund_owner, fund_client):\n  """Transfer tokens between users."""\n  token = create_token(web3, deployer, "Telos EVM rocks", "TELOS", 100_000 * 10 ** 18)\n\n  # Move 10 tokens from deployer to user1\n  token.functions.transfer(fund_owner, 10 * 10 ** 18).transact({"from": deployer})\n  assert token.functions.balanceOf(fund_owner).call() == 10 * 10 ** 18\n\n  # Move 10 tokens from deployer to user1\n  token.functions.transfer(fund_client, 6 * 10 ** 18).transact({"from": fund_owner})\n  assert token.functions.balanceOf(fund_owner).call() == 4 * 10 ** 18\n  assert token.functions.balanceOf(fund_client).call() == 6 * 10 ** 18\n```\n\n[See full example](https://github.com/tradingstrategy-ai/web3-ethereum-defi/blob/master/tests/test_token.py).\n\n[For more information how to user Web3.py in testing, see Web3.py documentation](https://web3py.readthedocs.io/en/stable/examples.html#contract-unit-tests-in-python).\n\n## Uniswap v2 trade example\n\n```python\nimport pytest\nfrom web3 import Web3\nfrom web3.contract import Contract\n\nfrom eth_defi.uniswap_v2.deployment import UniswapV2Deployment, deploy_trading_pair, FOREVER_DEADLINE\n\n\ndef test_swap(web3: Web3, deployer: str, fund_owner, uniswap_v2: UniswapV2Deployment, weth: Contract, usdc: Contract):\n    """User buys WETH on Uniswap v2 using mock USDC."""\n\n    # Create the trading pair and add initial liquidity\n    deploy_trading_pair(\n        web3,\n        deployer,\n        uniswap_v2,\n        weth,\n        usdc,\n        10 * 10 ** 18,  # 10 ETH liquidity\n        17_000 * 10 ** 18,  # 17000 USDC liquidity\n    )\n\n    router = uniswap_v2.router\n\n    # Give user_1 500 dollars to buy ETH and approve it on the router\n    usdc_amount_to_pay = 500 * 10 ** 18\n    usdc.functions.transfer(fund_owner, usdc_amount_to_pay).transact({"from": deployer})\n    usdc.functions.approve(router.address, usdc_amount_to_pay).transact({"from": fund_owner})\n\n    # Perform a swap USDC->WETH\n    path = [usdc.address, weth.address]  # Path tell how the swap is routed\n    # https://docs.uniswap.org/protocol/V2/reference/smart-contracts/router-02#swapexacttokensfortokens\n    router.functions.swapExactTokensForTokens(\n        usdc_amount_to_pay,\n        0,\n        path,\n        fund_owner,\n        FOREVER_DEADLINE,\n    ).transact({\n        "from": fund_owner\n    })\n\n    # Check the user_1 received ~0.284 ethers\n    assert weth.functions.balanceOf(fund_owner).call() / 1e18 == pytest.approx(0.28488156127668085)\n```\n\n[See the full example](https://github.com/tradingstrategy-ai/web3-ethereum-defi/blob/master/tests/test_uniswap_v2_pair.py).\n\n## Uniswap v2 price estimation example\n\n```python\n# Create the trading pair and add initial liquidity\ndeploy_trading_pair(\n    web3,\n    deployer,\n    uniswap_v2,\n    weth,\n    usdc,\n    1_000 * 10**18,  # 1000 ETH liquidity\n    1_700_000 * 10**18,  # 1.7M USDC liquidity\n)\n\n# Estimate the price of buying 1 ETH\nusdc_per_eth = estimate_buy_price_decimals(\n    uniswap_v2,\n    weth.address,\n    usdc.address,\n    Decimal(1.0),\n)\nassert usdc_per_eth == pytest.approx(Decimal(1706.82216820632059904))\n```\n\n# How to use the library in your Python project\n\nAdd `web3-ethereum-defi` as a development dependency:\n\nUsing [Poetry](https://python-poetry.org/):\n\n```shell\n# Data optional dependencies include pandas and gql, needed to fetch Uniswap v3 data\npoetry add -D "web3-ethereum-defi[data]"\n```\n\n# Documentation\n\n- [Browse API documentation](https://web3-ethereum-defi.readthedocs.io/).\n- [Browse tutorials](https://web3-ethereum-defi.readthedocs.io/tutorials/index.html).\n\n# Development and contributing\n\n- [Read development instructions](https://web3-ethereum-defi.readthedocs.io/development.html).\n\n# Version history\n\n- [Read changelog](https://github.com/tradingstrategy-ai/web3-ethereum-defi/blob/master/CHANGELOG.md).\n- [See releases](https://pypi.org/project/web3-ethereum-defi/#history).\n\n# Support \n\n- [Join Discord for any questions](https://tradingstrategy.ai/community).\n\n# Social media\n\n- [Follow on Twitter](https://twitter.com/TradingProtocol)\n- [Follow on Telegram](https://t.me/trading_protocol)\n- [Follow on LinkedIn](https://www.linkedin.com/company/trading-strategy/)\n\n# History\n\n[Originally created for Trading Strategy](https://tradingstrategy.ai). \n[Originally the package was known as eth-hentai](https://raw.githubusercontent.com/tradingstrategy-ai/web3-ethereum-defi/master/docs/source/_static/hentai_teacher_mikisugi_by_ilmaris_d6tjrn8-fullview.jpg).\n\n# License \n\nMIT\n',
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

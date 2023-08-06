<br/>
<br/>

<h1>The Python SDK for Paloma</h1>
<br/>

<p><sub>(Unfamiliar with Paloma?  <a href="https://docs.palomachain.com">Check out the Paloma Docs</a>)</sub></p>

  

<p>
  <a href="https://docs.palomachain.com"><strong>Explore the Docs »</strong></a>
  ·
  <a href="https://github.com/palomachain/paloma.py">GitHub Repository</a>
</p></div>

The Paloma Software Development Kit (SDK) in Python is a simple library toolkit for building software that can interact with the Paloma blockchain and provides simple abstractions over core data structures, serialization, key management, and API request generation.

## Features

- Written in Python with extensive support libraries
- Versatile support for key management solutions
- Exposes the Paloma API through LCDClient

<br/>

# Table of Contents

- [API Reference](#api-reference)
- [Getting Started](#getting-started)
  - [Requirements](#requirements)
  - [Installation](#installation)
  - [Dependencies](#dependencies)
  - [Tests](#tests)
  - [Code Quality](#code-quality)
- [Usage Examples](#usage-examples)
  - [Getting Blockchain Information](#getting-blockchain-information)
    - [Async Usage](#async-usage)
  - [Building and Signing Transactions](#building-and-signing-transactions)
    - [Example Using a Wallet](#example-using-a-wallet-recommended)
- [Contributing](#contributing)
  - [Reporting an Issue](#reporting-an-issue)
  - [Requesting a Feature](#requesting-a-feature)
  - [Contributing Code](#contributing-code)
  - [Documentation Contributions](#documentation-contributions)
- [License](#license)

<br/>

# API Reference

An intricate reference to the APIs on the Paloma SDK can be found <a href="https://docs.palomachain.com">here</a>.

<br/>

# Getting Started

A walk-through of the steps to get started with the Paloma SDK alongside a few use case examples are provided below. git ad

## Requirements

Paloma SDK requires <a href="https://www.python.org/downloads/">Python v3.7+</a>.

## Installation

<sub>**NOTE:** _All code starting with a `$` is meant to run on your terminal (a bash prompt). All code starting with a `>>>` is meant to run in a python interpreter, like <a href="https://pypi.org/project/ipython/">ipython</a>._</sub>

Paloma SDK can be installed (preferably in a `virtual environment` from PyPI using `pip`) as follows:
  
```
$ pip install -U paloma_sdk
```

<sub>_You might have `pip3` installed instead of `pip`; proceed according to your own setup._<sub>
  
❗ If you want to communicate with Paloma Classic, use paloma-sdk==2.x
  
## Dependencies

Paloma SDK uses <a href="https://python-poetry.org/">Poetry</a> to manage dependencies. To get set up with all the required dependencies, run:

```
$ pip install poetry
$ poetry install
```

## Tests

Paloma SDK provides extensive tests for data classes and functions. To run them, after the steps in [Dependencies](#dependencies):

```
$ make test
```

## Code Quality

Paloma SDK uses <a href="https://black.readthedocs.io/en/stable/">Black</a>, <a href="https://isort.readthedocs.io/en/latest/">isort</a>, and <a href="https://mypy.readthedocs.io/en/stable/index.html">Mypy</a> for checking code quality and maintaining style. To reformat, after the steps in [Dependencies](#dependencies):

```
$ make qa && make format
```

<br/>

# Usage Examples

Paloma SDK can help you read block data, sign and send transactions, deploy and interact with contracts, and many more.
The following examples are provided to help you get started. Use cases and functionalities of the Paloma SDK are not limited to the following examples and can be found in full <a href="https://paloma-money.github.io/paloma.py/index.html">here</a>.

In order to interact with the Paloma blockchain, you'll need a connection to a Paloma node. This can be done through setting up an LCDClient (The LCDClient is an object representing an HTTP connection to a Paloma LCD node.):

```
>>> from paloma_sdk.client.lcd import LCDClient
>>> paloma = LCDClient(chain_id="<CHECK DOCS FOR LATEST TESTNET>", url="https://testnet.palomaswap.com")
```

## Getting Blockchain Information

Once properly configured, the `LCDClient` instance will allow you to interact with the Paloma blockchain. Try getting the latest block height:

```
>>> paloma.tendermint.block_info()['block']['header']['height']
```

`'1687543'`

### Async Usage

If you want to make asynchronous, non-blocking LCD requests, you can use AsyncLCDClient. The interface is similar to LCDClient, except the module and wallet API functions must be awaited.

<pre><code>
>>> import asyncio 
>>> from paloma_sdk.client.lcd import AsyncLCDClient

>>> async def main():
      <strong>paloma = AsyncLCDClient("https://testnet.palomaswap.com", "<CHECK DOCS FOR LATEST TESTNET>")</strong>
      total_supply = await paloma.bank.total()
      print(total_supply)
      <strong>await paloma.session.close # you must close the session</strong>

>>> asyncio.get_event_loop().run_until_complete(main())
</code></pre>

## Building and Signing Transactions

If you wish to perform a state-changing operation on the Paloma blockchain such as sending tokens, swapping assets, withdrawing rewards, or even invoking functions on smart contracts, you must create a **transaction** and broadcast it to the network.
Paloma SDK provides functions that help create StdTx objects.

### Example Using a Wallet (_recommended_)

A `Wallet` allows you to create and sign a transaction in a single step by automatically fetching the latest information from the blockchain (chain ID, account number, sequence).

Use `LCDClient.wallet()` to create a Wallet from any Key instance. The Key provided should correspond to the account you intend to sign the transaction with.
  
<sub>**NOTE:** *If you are using MacOS and got an exception 'bad key length' from MnemonicKey, please check your python implementation. if `python3 -c "import ssl; print(ssl.OPENSSL_VERSION)"` returns LibreSSL 2.8.3, you need to reinstall python via pyenv or homebrew.*</sub>

```
>>> from paloma_sdk.client.lcd import LCDClient
>>> from paloma_sdk.key.mnemonic import MnemonicKey

>>> mk = MnemonicKey(mnemonic=MNEMONIC)
>>> paloma = LCDClient("https://testnet.palomaswap.com", "<CHECK DOCS FOR LATEST TESTNET>")
>>> wallet = paloma.wallet(mk)
```

Once you have your Wallet, you can simply create a StdTx using `Wallet.create_and_sign_tx`.

```
>>> from paloma_sdk.core.fee import Fee
>>> from paloma_sdk.core.bank import MsgSend
>>> from paloma_sdk.client.lcd.api.tx import CreateTxOptions

>>> tx = wallet.create_and_sign_tx(CreateTxOptions(
        msgs=[MsgSend(
            wallet.key.acc_address,
            RECIPIENT,
            "1000000ugrain"    # send 1 grain
        )],
        memo="test transaction!",
        fee=Fee(200000, "120000ugrain")
    ))
```

You should now be able to broadcast your transaction to the network.

```
>>> result = paloma.tx.broadcast(tx)
>>> print(result)
```

<br/>

# Contributing

Community contribution, whether it's a new feature, correction, bug report, additional documentation, or any other feedback is always welcome. Please read through this section to ensure that your contribution is in the most suitable format for us to effectively process.

<br/>

## Reporting an Issue

First things first: **Do NOT report security vulnerabilities in public issues!** Please disclose responsibly by submitting your findings to the [Paloma Bugcrowd submission form](https://www.paloma.money/bugcrowd). The issue will be assessed as soon as possible.
If you encounter a different issue with the Python SDK, check first to see if there is an existing issue on the <a href="https://github.com/paloma-money/paloma-sdk-python/issues">Issues</a> page, or if there is a pull request on the <a href="https://github.com/paloma-money/paloma-sdk-python/pulls">Pull requests</a> page. Be sure to check both the Open and Closed tabs addressing the issue.

If there isn't a discussion on the topic there, you can file an issue. The ideal report includes:

- A description of the problem / suggestion.
- How to recreate the bug.
- If relevant, including the versions of your:
  - Python interpreter
  - Paloma SDK
  - Optionally of the other dependencies involved
- If possible, create a pull request with a (failing) test case demonstrating what's wrong. This makes the process for fixing bugs quicker & gets issues resolved sooner.
  </br>

## Requesting a Feature

If you wish to request the addition of a feature, please first check out the <a href="https://github.com/paloma-money/paloma-sdk-python/issues">Issues</a> page and the <a href="https://github.com/paloma-money/paloma-sdk-python/pulls">Pull requests</a> page (both Open and Closed tabs). If you decide to continue with the request, think of the merits of the feature to convince the project's developers, and provide as much detail and context as possible in the form of filing an issue on the <a href="https://github.com/paloma-money/paloma-sdk-python/issues">Issues</a> page.

<br/>

## Contributing Code

If you wish to contribute to the repository in the form of patches, improvements, new features, etc., first scale the contribution. If it is a major development, like implementing a feature, it is recommended that you consult with the developers of the project before starting the development to avoid duplicating efforts. Once confirmed, you are welcome to submit your pull request.
</br>

### For new contributors, here is a quick guide:

1. Fork the repository.
2. Build the project using the [Dependencies](#dependencies) and [Tests](#tests) steps.
3. Install a <a href="https://virtualenv.pypa.io/en/latest/index.html">virtualenv</a>.
4. Develop your code and test the changes using the [Tests](#tests) and [Code Quality](#code-quality) steps.
5. Commit your changes (ideally follow the <a href="https://github.com/angular/angular/blob/master/CONTRIBUTING.md#commit">Angular commit message guidelines</a>).
6. Push your fork and submit a pull request to the repository's `main` branch to propose your code.

A good pull request:

- Is clear and concise.
- Works across all supported versions of Python. (3.7+)
- Follows the existing style of the code base (<a href="https://pypi.org/project/flake8/">`Flake8`</a>).
- Has comments included as needed.
- Includes a test case that demonstrates the previous flaw that now passes with the included patch, or demonstrates the newly added feature.
- Must include documentation for changing or adding any public APIs.
- Must be appropriately licensed (MIT License).
  </br>

## Documentation Contributions

Documentation improvements are always welcome. The documentation files live in the [docs](./docs) directory of the repository and are written in <a href="https://docutils.sourceforge.io/rst.html">reStructuredText</a> and use <a href="https://www.sphinx-doc.org/en/master/">Sphinx</a> to create the full suite of documentation.
</br>
When contributing documentation, please do your best to follow the style of the documentation files. This means a soft limit of 88 characters wide in your text files and a semi-formal, yet friendly and approachable, prose style. You can propose your improvements by submitting a pull request as explained above.

### Need more information on how to contribute?

You can give this <a href="https://opensource.guide/how-to-contribute/#how-to-submit-a-contribution">guide</a> read for more insight.

<br/>

# License

This software is licensed under the MIT license. See [LICENSE](./LICENSE) for full disclosure.

© 2021 Paloma

<hr/>

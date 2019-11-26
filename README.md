[![license: GPL v3](https://img.shields.io/badge/license-GPLv3-blue.svg)](/LICENSE)
[![python](https://img.shields.io/badge/python-3.7-green.svg)]()
[![version](https://img.shields.io/badge/version-2019.7-ff69b4.svg)](/cereal/cereal/version.py)
[![build status](https://travis-ci.com/Icermli/cereal.svg?token=pojzrPMupy6Wy7FYdwHH&branch=master)](https://travis-ci.com/Icermli/cereal)
[![downloads](https://img.shields.io/github/downloads/Icermli/cereal/total.svg)]()
[![issues](https://img.shields.io/github/issues/Icermli/cereal.svg)](https://github.com/Icermli/cereal/issues)

# Cereal

Cereal is a Python library for exploring cryptocurrency markets.

CEREAL is a recursive acronym for Crypto ExploreR Even Analysis and Learn.

# How to use

```bash
cereal: a Python library for exploring cryptocurrency markets.
usage: cereal [--version] [--debug] [--config=<ph>] [--help]
           [--telegram] [<command>] [<args>...]

Options:
    -d, --debug           Show debugging info.
    -h, --help            Show this help screen.
    -v, --version         Show cereal version.
    -t, --telegram        Use telegram bot.
    -c, --config=<ph>     Path to config file.
```

Try `cereal --version` and `cereal --help` to see more information.

## Commend

- cereal deploy -- deploy vsys node to remote aws EC2 server
- cereal guard -- guard vsys node locally (restart node if height is not changed)
- cereal monitor -- monitor vsys address (if these addresses have new transaction)
- cereal ipmonitor -- monitor vsys node ip (if node of these ips are working properly)
- cereal chatbot -- start a chat bot on Telegram to ask some questions


# Test

Using `pytest` framework makes it easy to write small tests, yet scales to support complex functional testing for applications and libraries.

To execute it:

```
pytest
```

# Donate

[![Bitcoin Donate Button](https://icermli.github.io/cereal/donate/Bitcoin-Donate-button.png)](https://icermli.github.io/cereal/donate/)

# [Documentation](https://icermli.github.io/cereal/doc/build/)

View the [documentation](https://icermli.github.io/cereal/doc/build/)
for Cereal on Read the Docs.

To build the documentation yourself using [Sphinx](http://www.sphinx-doc.org/), run:

```
sphinx-build -b html doc/source/ doc/build/
```

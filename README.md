# rinse

[![PyPI version](https://badge.fury.io/py/rinstall.svg)](https://badge.fury.io/py/rinstall)
[![OS](https://img.shields.io/badge/OS-Windows%2C%20Linux-blue)](https://github.com/datasnakes/rinse)

Rinse, short for R installer, is a CLI (command line interface) for installing R on Linux, Windows, and MacOS from source. It exists as a standalone project and as a component of [beRi](https://github.com/datasnakes/beRi).

Currently works with:

* __Repos__: CRAN
* __Installation Methods__: Source
* __Supported OS__: Linux, Windows, MacOS
* __Permission Level__: Sudo, Non-sudo

## Project Background

Rinse is currently a simple installer for the latest version of R. This includes installing/uninstalling R from source, managing R dependencies, and switching between versions of R. Creating a CLI for users, who may not be able to access R's gui or Rstudio on servers (HPC or personal), is the main inspiration for this project. Implementing rinse for Windows will be the main goal at hackseq19.

In the future, installing [Microsoft R Open](https://mran.microsoft.com/open) or [other R implementations](https://en.wikipedia.org/wiki/R_(programming_language)#Implementations) will also be considered. We would also like to implement features similar to [pyvenv](https://github.com/pyenv/pyenv/blob/master/COMMANDS.md). 

## Installation

Currently, rinse is in the alpha stage of development.  The latest release can be installed from PyPI
or the development version can be installed from the *dev-master* branch on GitHub.

### Install the Latest PyPi Release

```bash
pip install rinstall
```

### Development Version Install

1. Create a virual environment called `rinse` using your tool of choice: `pyenv`, `poetry`, `pipenv`, `virtualenv`, `virtualenvwrapper`, `conda`, `pew`, etc.

2. Install poetry within your virtual environment:

```console
[ $ ] python -m venv ~/.env/rinse
[ $ ] source ~/.env/rinse/bin/activate
(rinse) [ $ ] pip install poetry
...
(rinse) [ $ ] mkdir GitHub; cd Github
(rinse) [ ~/Github $ ] git clone -b dev-master https://github.com/datasnakes/rinse.git
(rinse) [ ~/Github $ ] cd rinse
(rinse) [ ~/Github/rinse $ ] poetry install
...
```

## Simple Usage

### Initializing Rinse

In order to use rinse, it must first be initialized:

```console
(rinse) [ ~/Github/rinse $ ] rinse init
```

The initialization step is necessary to create proper installation folders to store your R installs.

### Installing R

You can install the latest version of R into your home directory with a single short command:

```console
(rinse) [ ~/Github/rinse $ ] rinse install
# or
(rinse) [ ~/Github/rinse $ ] rinse install latest
# or
(rinse) [ ~/Github/rinse $ ] rinse install 3.5.3
```

**Note**:  _Be aware that R can take around 20 minutes to install._

## Alternative Usage

First note:

```console
(rinse) [ ~/Github/rinse $ ] rinse configure --help # configure script help (./configure --help)
# is different from
(rinse) [ ~/Github/rinse $ ] rinse configure --chelp # rinse cli help
```

Here's how you can perform various installation steps of R:

```console
(rinse) [ ~/Github/rinse $ ] rinse configure 3.5.3
(rinse) [ ~/Github/rinse $ ] rinse make --check 3.5.3
(rinse) [ ~/Github/rinse $ ] rinse make --install 3.5.3 
(rinse) [ ~/Github/rinse $ ] rinse make --install-tests 3.5.3
(rinse) [ ~/Github/rinse $ ] rinse test --check --check-devel --check-all 3.5.3
```

Downloading Rtools with the latest R version on Windows:

```console
(rinse) [ ~/Github/rinse $ ] rinse configure --with-rtools=True
```

## Help

If you need help with using rinse, please [submit an issue](https://github.com/datasnakes/rinse/issues/new), and we will respond as soon as we can.

## Maintainers

* Kristen Bystrom
* Rob Gilmore
* Bruno Grande
* Shaurita Hutchins
* Roshan Pawar
* Cedric Wang

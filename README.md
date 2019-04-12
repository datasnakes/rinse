# rinse

A CLI for installing R.

Currently works with:

* __Repos__: CRAN
* __Installation Methods__: Source
* __Supported OS__: Linux
* __Permission Level__: Sudo, Non-sudo

Will work with:

* __Repos__: Microsoft R Open
* __Installation Methods__: Spack, Local
* __Supported OS__: MacOS, Windows

## Installation

Currently, rinse is in the alpha stage of development.  The latest release can be installed from PyPI
or the development version can be installed from the *dev-master* branch on GitHub.

### Latest Release

```console
[ $ ] pip install rinstall
```
### Development Version

Create a VE called `rinse` using your tool of choice:

* pyenv
* poetry
* pipenv
* virtualenv
* virtualenvwrapper
* conda
* pew
* python -m venv

After making a VE install poetry into it:

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

### Initialize Rinse

Before you do anything, rinstall must be initialized or you will get an error:

```console
(rinse) [ ~/Github/rinse $ ] rinse init
```

## Simple Usage

You can install the latest version of R into your home directory with a single short command:

```console
(rinse) [ ~/Github/rinse $ ] rinse install
# or
(rinse) [ ~/Github/rinse $ ] rinse install latest
# or
(rinse) [ ~/Github/rinse $ ] rinse install 3.5.3
```

**Note**:  _Be aware that R can take around 20 minutes to install._

## Alternate Usage

First note:

```console
(rinse) [ ~/Github/rinse $ ] rinse configure --help # configure script help (./configure --help)
# is different from
(rinse) [ ~/Github/rinse $ ] rinse configure --chelp # rinse cli help
```

Here's how you can work through various installation steps:
```console
(rinse) [ ~/Github/rinse $ ] rinse configure 3.5.3
(rinse) [ ~/Github/rinse $ ] rinse make --check 3.5.3
(rinse) [ ~/Github/rinse $ ] rinse make --install 3.5.3 
(rinse) [ ~/Github/rinse $ ] rinse make --install-tests 3.5.3
(rinse) [ ~/Github/rinse $ ] rinse test --check --check-devel --check-all 3.5.3
```

## Maintainers

* Kristen Bystrom
* Rob Gilmore
* Bruno Grande
* Shaurita Hutchins

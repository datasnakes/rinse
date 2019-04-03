# rinse

A configurable installer CLI for installing R.

* __Repos__: CRAN, MRAN, etc.
* __Methods__: Source, Spack, Local
* __Permission__: Sudo, Non-sudo

## Installation

Currently rinse is not on PyPi.  For now you will have to do the following:

### Create a new Virutal Environment

Create a VE called `rinse` using your tool of choice:

* pyenv
* poetry
* pipenv
* virtualenv
* virtualenvwrapper
* conda
* pew
* python -m venv

After making a VE install poetry into it

```console
[ $ ] python -m venv ~/.env/rinse
[ $ ] source ~/.env/rinse/bin/activate
(rinse) [ $ ] pip install poetry
...
(rinse) [ $ ] mkdir GitHub; cd Github
(rinse) [ ~/Github $ ] git clone https://github.com/datasnakes/rinse.git
(rinse) [ ~/Github $ ] cd rinse
(rinse) [ ~/Github/rinse $ ] poetry install
...
```

### Initialize Rinse

Before you do anyting rinse must be initialized or you will get an error:

```console
(rinse) [ ~/Github/rinse $ ] rinse init
```

## Simple Usage

You can install the latest version of R into your home directory with a single short command.

```console
(rinse) [ ~/Github/rinse $ ] rinse install
# or
(rinse) [ ~/Github/rinse $ ] rinse install latest
# or
(rinse) [ ~/Github/rinse $ ] rinse install 3.5.3

```

## Maintainers

* Shaurita Hutchins
* Rob Gilmore
* Bruno Grande

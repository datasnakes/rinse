# rinse

A configurable installer CLI for installing R from source (sudo and non-sudo).


## Usage

You can install the latest version of R into your home directory with a single short command:

```bash
$ rinse
Running: bash /tmp/tmpcphk7y1l/script.sh
Downloading R...
Extracting R...
Configuring R...
Compiling R...
Installing R...
```

If you're interested in installing a different version of R in a specific directory, you can do that too!

```
$ rinse --version 3.4.2 --path ~/R-3.4.2
```


## Installation

Until we publish rinse as a Python package, you can install it locally using the following commands. 

```bash
# Install pip
curl https://bootstrap.pypa.io/get-pip.py -o get-pip.py
python3 get-pip.py --user
# Install poetry
pip install --user poetry
# Install rinse
wget https://github.com/datasnakes/rinse/archive/master.zip
unzip master.zip
cd rinse-master
poetry install
poetry build -f wheel
pip install --user dist/rinse-0.1.0-py3-none-any.whl
```

## Maintainers

* Shaurita Hutchins
* Rob Gilmore
* Bruno Grande

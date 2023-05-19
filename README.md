# Runduk AI

This is a project which helps you to draft heroes for you team in Dota 2

## Installation

### Install pyenv

Linux:
```shell
curl https://pyenv.run | bash
```

Mac:
```shell
brew update
brew install pyenv
```

All Platforms:
```shell
pyenv install 3.10.8
pyenv rehash
pyenv local 3.10.8
pyenv global 3.10.8
```

### Install Project

Note, if your poetry commands hang, try this:

    export PYTHON_KEYRING_BACKEND=keyring.backends.null.Keyring

1. Install Poetry

```shell
curl -sSL https://install.python-poetry.org | python3 -
```

2. Install the project

linux:
```shell
poetry install
```

## How to use

1. Enter the interactive shell

```shell
poetry shell
```

2. Launch `main.py` with Python Tkinter GUI 

```shell
python picker/app/old_python_gui/main.py
```

3. Use the program! The interface is ugly but should be self-explanatory.
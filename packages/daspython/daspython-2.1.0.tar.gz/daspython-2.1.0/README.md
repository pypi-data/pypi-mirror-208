# Welcome to the DAS Python package

The [Royal Netherlands Institute for Sea Research](https://www.nioz.nl) has its data management system to help scientists archive and access their data. This tool is called: **Data Archive System (DAS)** and this package is its Python client.

_*NOTE: This package requires Python 3.11 and plus*_

# To install using pip

```
    $ pip install daspython
```

# To install this package locally use the following commands:

## Create a virtual environment first:

### Install virtualenv if not installed.
```
    $ pip install virtualenv
```

### Create the virtual enviroment
```
    $ virtualenv .venv
```

### Activate your virtual environment (for Windows)
```
    $ .\.venv\Scripts\activate.ps1   
```

### Deactivate your virtual environment (for Windows)
```
    $ deactivate
```


### Now install the dependencies

```powershell
    $ pip install -r .\requirements.txt
```

The best way to see how each method is used is visiting out [automated test scripts](https://git.nioz.nl/ict-projects/das-python/-/tree/master/tests) page.

# Authentication

Use this class to authenticate and keep your token that will be needed to use with all other service classes.

##### Usage

```python
from daspython.auth.authenticate import DasAuth

auth = DasAuth('DAS url', 'Your user name', 'Your password')

if (auth.authenticate()):
    print('You are connected ...')    
```

# Unit Tests

```
python -m unittest tests/test_something.py
```

## Deploying this package:

```
$ pip install twine
```
### Install twine
```
twine upload dist/*
```
Than follow the instructions to publish/upload the distribution files to pypi.org
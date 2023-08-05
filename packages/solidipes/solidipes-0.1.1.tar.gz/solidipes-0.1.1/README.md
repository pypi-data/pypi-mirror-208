

# Solidipes

_Python package for the DCSM project_

[![](https://readthedocs.org/projects/solidipes/badge/?version=latest)](http://solidipes.readthedocs.io/)

See the package's documentation on [Read the Docs](http://solidipes.readthedocs.io/).

<img src="https://gitlab.com/dcsm/solidipes/-/raw/dev/logos/solidipes.jpg" width="200px" height="200px">


# Installation

## As regular user

```
pip install solidipes
```


## As developer

If you intend to implement new features into the code (like implementing a new reader for a specific file format or a new type of report), you need to get the source code of Solidipes.


### Dependencies

- Python (3.8 minimum)
- make
- [Poetry](https://python-poetry.org/docs/#installation)

```
git clone https://gitlab.com/dcsm/solidipes.git
cd solidipes
make install
```

This will install Solidipes as well as all the development dependencies.


# Usage from the command line

To see a list of all available commands, run
```
solidipes --help
```

Consult the documentation in the [Getting started](https://solidipes.readthedocs.io/en/latest/src/getting_started.html#usage-from-the-command-line) section for next steps.

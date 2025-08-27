This project contains C3PO (Collaborative Code Coupling PlatfOrm) sources.

## Contact ##

 Cyril PATRICOT (cyril.patricot@cea.fr)

## Description ##

It is composed of 3 folders:
- **sources** with the sources of C3PO (Python only),
- **doc** with the documentation (Doxygen),
- **tests** with basic tests (stand-alone tests that do not require codes).

## Installation ##

C3PO package can be installed using pip from **sources** directory.

For example the following line installs the package in developer mode (modifiable sources):
```sh
pip install --user -e .
```

## Documentation ##

C3PO's Sphinx documentation can be generated from **doc** directory using:
```sh
make html
```

> **WARNING**: To generate C3PO documentation, use a Python version higher than 3.11.

Python modules `graphviz`, `sphinx-rtd-theme` and `sphinx` have to be installed using pip:
```sh
pip install -r ./doc/requirements.txt
```

It can also be found here: https://salome-c3po.readthedocs.io .

## Tests ##

Tests are based on pytest.
C3PO's tests can be run using:
```sh
./run_tests.sh
```

The environment (with C3PO, MEDCoupling and mpi4py) must be set before launching the tests.
See the documentation of the script (./run_test.sh --help) for available options.

## Python style conventions ##

This project use the code linter [Pylint](https://www.pylint.org/) for coding
conventions and [NumPy Style Python Docstrings](https://numpydoc.readthedocs.io/en/latest/format.html) for docstrings formating.

The conventions used by C3PO are defined in the files sources/.pylintrc.

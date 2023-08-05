[![Eclipse VOLTTRON™](https://img.shields.io/badge/Eclips%20VOLTTRON--red.svg)](https://volttron.readthedocs.io/en/latest/)
![Python 3.10](https://img.shields.io/badge/python-3.10-blue.svg)
![Python 3.11](https://img.shields.io/badge/python-3.11-blue.svg)
[![Run Pytests](https://github.com/eclipse-volttron/volttron-lib-base-historian/actions/workflows/run-tests.yml/badge.svg)](https://github.com/eclipse-volttron/volttron-lib-base-historian/actions/workflows/run-tests.yml)
[![pypi version](https://img.shields.io/pypi/v/volttron-lib-base-historian.svg)](https://pypi.org/project/volttron-lib-base-historian/)

VOLTTRON base historian framework that provide common functions such as caching, error handling, input validation etc. This historian cannot be used as agent as is. VOLTTRON historian agents can be created by subclassing the [BaseHistorian class](https://github.com/eclipse-volttron/volttron-lib-base-historian/blob/develop/src/historian/base/base_historian.py) in this library.

## Requirements

 - Python >= 3.10

## Installation

This library can be installed using ```pip install volttron-lib-base-historian```. However, this is not necessary. Any 
historian agent that uses this library will automatically install it as part of its installation. For example, 
installing [SQLiteHistorian](https://github.com/eclipse-volttron/volttron-sqlitehistorian) will automatically install 
volttron-lib-base-historian into the same python environment

## Development

Please see the following for contributing guidelines [contributing](https://github.com/eclipse-volttron/volttron-core/blob/develop/CONTRIBUTING.md).

Please see the following helpful guide about [developing modular VOLTTRON agents](https://github.com/eclipse-volttron/volttron-core/blob/develop/DEVELOPING_ON_MODULAR.md)

# Disclaimer Notice

This material was prepared as an account of work sponsored by an agency of the
United States Government.  Neither the United States Government nor the United
States Department of Energy, nor Battelle, nor any of their employees, nor any
jurisdiction or organization that has cooperated in the development of these
materials, makes any warranty, express or implied, or assumes any legal
liability or responsibility for the accuracy, completeness, or usefulness or any
information, apparatus, product, software, or process disclosed, or represents
that its use would not infringe privately owned rights.

Reference herein to any specific commercial product, process, or service by
trade name, trademark, manufacturer, or otherwise does not necessarily
constitute or imply its endorsement, recommendation, or favoring by the United
States Government or any agency thereof, or Battelle Memorial Institute. The
views and opinions of authors expressed herein do not necessarily state or
reflect those of the United States Government or any agency thereof.

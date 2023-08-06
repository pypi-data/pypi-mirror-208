# Platform Driver Agent

![Passing?](https://github.com/eclipse-volttron/volttron-platform-driver/actions/workflows/run-tests.yml/badge.svg)
[![pypi version](https://img.shields.io/pypi/v/volttron-platform-driver.svg)](https://pypi.org/project/volttron-platform-driver/)


The Platform Driver agent is a special purpose agent a user can install on the platform to manage communication of the platform with devices. The Platform driver features a number of endpoints for collecting data and sending control signals using the message bus and automatically publishes data to the bus on a specified interval.

# Requires

* python >= 3.10
* volttron >= 10.0
* volttron-lib-base-driver

# Documentation
More detailed documentation can be found on [ReadTheDocs](https://volttron.readthedocs.io/en/modular/). The RST source
of the documentation for this component is located in the "docs" directory of this repository.

# Installation


Before installing, VOLTTRON should be installed and running.  Its virtual environment should be active.
Information on how to install of the VOLTTRON platform can be found
[here](https://github.com/eclipse-volttron/volttron-core).

Install and start the volttron-platform-driver.

```shell
vctl install volttron-platform-driver --vip-identity platform.driver --start
```

View the status of the installed agent

```shell
vctl status
```

# Development

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

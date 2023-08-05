# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['fieldedge_utilities',
 'fieldedge_utilities.ip',
 'fieldedge_utilities.microservice']

package_data = \
{'': ['*']}

install_requires = \
['ifaddr>=0.1.7,<0.2.0',
 'paho-mqtt>=1.6.1,<2.0.0',
 'pyserial>=3.5,<4.0',
 'python-dotenv>=0.19.1,<0.20.0']

setup_kwargs = {
    'name': 'fieldedge-utilities',
    'version': '0.22.6',
    'description': 'Utilities package for the FieldEdge project.',
    'long_description': '# Inmarsat FieldEdge Utilities\n\nInmarsat FieldEdge project supports *Internet of Things* (**IoT**) using\nsatellite communications technology. Generally this library is meant to be used\non single board computers capable of running Debian Linux.\n\n>*While the authors recognize Python has several shortcomings for embedded use,*\n*it provides a useful learning template.*\n\nThis library available on [**PyPI**](https://pypi.org/project/fieldedge-utilities/)\nprovides:\n\n* A common **`logger`** format and wrapping file facility with UTC timestamps.\n* A **`timer.RepeatingTimer`** utility (thread) that can be started, stopped,\nrestarted, and interval changed.\n* A simplified **`mqtt`** client that automatically (re)onnects\n(by default to a local `fieldedge-broker`).\n* Helper functions for managing files and **`path`** on different OS.\n* An interface for the FieldEdge **`hostpipe`** service for sending host\ncommands from a Docker container, with request/result captured in a logfile.\n* Helper functions **`ip.interfaces`** for finding and validating IP interfaces\nand addresses/subnets.\n* A defined set of common **`ip.protocols`** used for packet analysis and\nsatellite data traffic optimisation.\n* Helpers for managing **`serial`** ports on a host system.\n* Utilities for converting **`timestamp`**s between unix and ISO 8601\n* **`properties`** manipulation and conversion between JSON and PEP style,\nand derived from classes or instances.\n* Classes useful for implementing **`microservice`**s based on MQTT\ninter-service communications and task workflows:\n    * **`interservice`** communications tasks and searchable queue.\n    * **`microservice`** class for consistent abstraction and interaction.\n    * **`msproxy`** microservice proxy class form a kind of twin of another\n    microservice, as a child of a microservice.\n    * **`feature`** class as a child of a microservice, with routing of MQTT\n    topics and messages and interaction with a simple task queue.\n    * **`propertycache`** concept for caching frequently referenced object\n    properties where the query may take time.\n    * **`subscriptionproxy`** allows cascading of received MQTT messages to\n    multiple modules within a project framing a microservice.\n\n[Docmentation](https://inmarsat-enterprise.github.io/fieldedge-utilities/)\n',
    'author': 'geoffbrucepayne',
    'author_email': 'geoff.bruce-payne@inmarsat.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/inmarsat-enterprise/fieldedge-utilities',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.7,<4.0',
}


setup(**setup_kwargs)

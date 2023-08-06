# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['sqlalchemy_exasol']

package_data = \
{'': ['*']}

install_requires = \
['packaging>=21.3',
 'pyexasol>=0.25.1,<0.26.0',
 'pyodbc>=4.0.34,<5.0.0',
 'sqlalchemy>=1.4,<1.4.45']

extras_require = \
{'turbodbc': ['turbodbc==4.5.4']}

entry_points = \
{'sqlalchemy.dialects': ['exa.pyodbc = '
                         'sqlalchemy_exasol.pyodbc:EXADialect_pyodbc',
                         'exa.turbodbc = '
                         'sqlalchemy_exasol.turbodbc:EXADialect_turbodbc']}

setup_kwargs = {
    'name': 'sqlalchemy-exasol',
    'version': '4.4.0',
    'description': 'EXASOL dialect for SQLAlchemy',
    'long_description': 'SQLAlchemy Dialect for EXASOL DB\n================================\n\n\n.. image:: https://github.com/exasol/sqlalchemy_exasol/workflows/CI/badge.svg?branch=master\n    :target: https://github.com/exasol/sqlalchemy_exasol/actions?query=workflow%3ACI\n     :alt: CI Status\n\n.. image:: https://img.shields.io/pypi/v/sqlalchemy_exasol\n     :target: https://pypi.org/project/sqlalchemy-exasol/\n     :alt: PyPI Version\n\n.. image:: https://img.shields.io/pypi/pyversions/sqlalchemy-exasol\n    :target: https://pypi.org/project/sqlalchemy-exasol\n    :alt: PyPI - Python Version\n\n.. image:: https://img.shields.io/badge/exasol-7.1.9%20%7C%207.0.18-green\n    :target: https://www.exasol.com/\n    :alt: Exasol - Supported Version(s)\n\n.. image:: https://img.shields.io/badge/code%20style-black-000000.svg\n    :target: https://github.com/psf/black\n    :alt: Formatter - Black\n\n.. image:: https://img.shields.io/badge/imports-isort-ef8336.svg\n    :target: https://pycqa.github.io/isort/\n    :alt: Formatter - Isort\n\n.. image:: https://img.shields.io/badge/pylint-5.8-yellow\n    :target: https://github.com/PyCQA/pylint\n    :alt: Pylint\n\n.. image:: https://img.shields.io/pypi/l/sqlalchemy-exasol\n     :target: https://opensource.org/licenses/BSD-2-Clause\n     :alt: License\n\n.. image:: https://img.shields.io/github/last-commit/exasol/sqlalchemy-exasol\n     :target: https://pypi.org/project/sqlalchemy-exasol/\n     :alt: Last Commit\n\n.. image:: https://img.shields.io/pypi/dm/sqlalchemy-exasol\n    :target: https://pypi.org/project/sqlalchemy-exasol\n    :alt: PyPI - Downloads\n\n\nHow to get started\n------------------\n\nWe assume you have a good understanding of (unix)ODBC. If not, make sure you\nread their documentation carefully - there are lot\'s of traps \U0001faa4 to step into.\n\nMeet the system requirements\n````````````````````````````\n\nOn Linux/Unix like systems you need:\n\n- Python\n- An Exasol DB (e.g. `docker-db <test_docker_image_>`_ or a `cloud instance <test_drive_>`_)\n- The packages unixODBC and unixODBC-dev >= 2.2.14\n- The Exasol `ODBC driver <odbc_driver_>`_\n- The ODBC.ini and ODBCINST.ini configurations files setup\n\nTurbodbc support\n````````````````\n\n.. warning::\n\n    Maintenance of this feature is on hold. Also it is very likely that turbodbc support will be dropped in future versions.\n\n- You can use Turbodbc with sqlalchemy_exasol if you use a python version >= 3.8.\n- Multi row update is not supported, see\n  `test/test_update.py <test/test_update.py>`_ for an example\n\n\nSetup your python project and install sqlalchemy-exasol\n```````````````````````````````````````````````````````\n\n.. code-block:: shell\n\n    $ pip install sqlalchemy-exasol\n\nfor turbodbc support:\n\n.. code-block:: shell\n\n    $ pip install sqlalchemy-exasol[turbodbc]\n\nTalk to the EXASOL DB using SQLAlchemy\n``````````````````````````````````````\n\n.. code-block:: python\n\n\tfrom sqlalchemy import create_engine\n\turl = "exa+pyodbc://A_USER:A_PASSWORD@192.168.1.2..8:1234/my_schema?CONNECTIONLCALL=en_US.UTF-8&driver=EXAODBC"\n\te = create_engine(url)\n\tr = e.execute("select 42 from dual").fetchall()\n\nto use turbodbc as driver:\n\n.. code-block:: python\n\n\tfrom sqlalchemy import create_engine\n\turl = "exa+turbodbc://A_USER:A_PASSWORD@192.168.1.2..8:1234/my_schema?CONNECTIONLCALL=en_US.UTF-8&driver=EXAODBC"\n\te = create_engine(url)\n\tr = e.execute("select 42 from dual").fetchall()\n\n\nThe dialect supports two types of connection urls creating an engine. A DSN (Data Source Name) mode and a host mode:\n\n.. list-table::\n\n   * - Type\n     - Example\n   * - DSN URL\n     - \'exa+pyodbc://USER:PWD@exa_test\'\n   * - HOST URL\n     - \'exa+pyodbc://USER:PWD@192.168.14.227..228:1234/my_schema?parameter\'\n\nFeatures\n++++++++\n\n- SELECT, INSERT, UPDATE, DELETE statements\n- you can even use the MERGE statement (see unit tests for examples)\n\nNotes\n+++++\n\n- Schema name and parameters are optional for the host url\n- At least on Linux/Unix systems it has proven valuable to pass \'CONNECTIONLCALL=en_US.UTF-8\' as a url parameter. This will make sure that the client process (Python) and the EXASOL driver (UTF-8 internal) know how to interpret code pages correctly.\n- Always use all lower-case identifiers for schema, table and column names. SQLAlchemy treats all lower-case identifiers as case-insensitive, the dialect takes care of transforming the identifier into a case-insensitive representation of the specific database (in case of EXASol this is upper-case as for Oracle)\n- As of Exasol client driver version 4.1.2 you can pass the flag \'INTTYPESINRESULTSIFPOSSIBLE=y\' in the connection string (or configure it in your DSN). This will convert DECIMAL data types to Integer-like data types. Creating integers is a factor three faster in Python than creating Decimals.\n\n.. _developer guide: https://github.com/exasol/sqlalchemy-exasol/blob/master/doc/developer_guide/developer_guide.rst\n.. _odbc_driver: https://docs.exasol.com/db/latest/connect_exasol/drivers/odbc/odbc_linux.htm\n.. _test_drive: https://www.exasol.com/test-it-now/cloud/\n.. _test_docker_image: https://github.com/exasol/docker-db\n\nDevelopment & Testing\n`````````````````````\nSee `developer guide`_\n\n',
    'author': 'Exasol AG',
    'author_email': 'opensource@exasol.com',
    'maintainer': 'None',
    'maintainer_email': 'None',
    'url': 'None',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'extras_require': extras_require,
    'entry_points': entry_points,
    'python_requires': '>=3.8,<4.0',
}


setup(**setup_kwargs)

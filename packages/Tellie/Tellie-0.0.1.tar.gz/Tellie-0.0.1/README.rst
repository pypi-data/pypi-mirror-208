=========================================================
Tellie CLI
=========================================================

Download and install the latest release::

    pip install -U tellie

.. contents::
   :local:
   :backlinks: top

Overview
--------

Tellie carries three completing uses:

(1) with command line arguments
(2) as an interactive shell
(3) as a client library


Key features:

- provides an API very close to the Tele API, through JSON-RPC and XML-RPC
- single executable ``tellie.py``, no external dependency
- helpers for ``search``, for data model introspection, etc...
- simplified syntax for search ``domain`` and ``fields``
- full API accessible on the ``Client.env`` environment
- the module can be imported and used as a library: ``from tellie import Client``
- supports Python 3.5 and above, and Python 2.7



.. _command-line:

Command line arguments
----------------------

Arguments::

    $ tellie --help

    Usage: tellie.py [options] [search_term_or_id [search_term_or_id ...]]

    Inspect data on Tele objects.  Use interactively or query a model (-m) and
    pass search terms or ids as positional parameters after the options.

    Options:
      --version             show program's version number and exit
      -h, --help            show this help message and exit
      -l, --list            list sections of the configuration
      --env=ENV             read connection settings from the given section
      -c CONFIG, --config=CONFIG
                            specify alternate config file (default: 'tellie.ini')
      --server=SERVER       full URL of the server (default:
                            http://localhost:9000/xmlrpc)
      -d DB, --db=DB        database
      -u USER, --user=USER  username
      -p PASSWORD, --password=PASSWORD
                            password, or it will be requested on login
      -m MODEL, --model=MODEL
                            the type of object to find
      -f FIELDS, --fields=FIELDS
                            restrict the output to certain fields (multiple
                            allowed)
      -i, --interact        use interactively; default when no model is queried
      -v, --verbose         verbose
    $ #


Example::

    $ tellie -d demo -m res.partner -f name -f lang 1
    "name","lang"
    "Your Company","en_US"

::

    $ tellie -d demo -m res.groups -f full_name 'id > 0'
    "full_name"
    "Administration / Access Rights"
    "Administration / Configuration"
    "Human Resources / Employee"
    "Usability / Multi Companies"
    "Usability / Extended View"
    "Usability / Technical Features"
    "Sales Management / User"
    "Sales Management / Manager"
    "Partner Manager"



.. _interactive-mode:

Interactive use
---------------

Edit ``tellie.ini`` and declare the environment(s)::

    [DEFAULT]
    scheme = http
    host = localhost
    port = 9000
    database = tele
    username = tele

    [demo]
    username = demo
    password = demo
    protocol = xmlrpc

    [demo_jsonrpc]
    username = demo
    password = demo
    protocol = jsonrpc

    [local]
    scheme = local
    options = -c /opt/tele/tele.conf --without-demo all


Connect to the Tele server::

    tellie --list
    tellie --env demo


This is a sample session::

    >>> env['res.users']
    <Model 'res.users'>
    >>> env['res.users'].search_count()
    4
    >>> crons = env['ir.cron'].with_context(active_test=False).search([])
    >>> crons.read('active name')
    [{'active': True, 'id': 5, 'name': 'Calendar: Event Reminder'},
     {'active': False, 'id': 4, 'name': 'Mail: Fetchmail Service'}]
    >>> #
    >>> env.modules('delivery')
    {'uninstalled': ['delivery', 'website_sale_delivery']}
    >>> env.upgrade('base')
    1 module(s) selected
    42 module(s) to process:
      to upgrade    account
      to upgrade    account_chart
      to upgrade    account_tax_include
      to upgrade    base
      ...
    >>> #


.. note::

   Use the ``--verbose`` switch to see what happens behind the scene.
   Lines are truncated at 79 chars.  Use ``-vv`` or ``-vvv`` to print
   more.


.. note::

   To preserve the history of commands when closing the session, first
   create an empty file in your home directory:
   ``touch ~/.tellie_history``

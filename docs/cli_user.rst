CLI User guide
==============

Using the command line tool to interact with IG Index platform.

General command line syntax
---------------------------

``PyGIndex`` command line tool is called ``pygi``.

The paramters are structured in the following way::

    $ pygi [options] <command> <action> [parameters]

Options
^^^^^^^

Options are applied to all commands and actions universally. You can use them
to control the behaviour of all commands, for example you can use ``--format``
option to set the format of the output that commands generate (text, json, etc).

This parameter is optional. If omitted, then default value will be used.

Object
^^^^^^

This parameter specifies what object to operate on. All interactions with the platform
are done by operating on "objects", such as ``instrument`` (for interation with
trading instruments), ``positions`` (for opening, closing, editing, and listing trading
positions), ``account`` (for account related settings) and so on.

Action
^^^^^^

Each object has a set of available actions that you can apply to it. For example,
if you want to find a particular instrument, you would call ``search`` action on
the ``instrument`` object::

    $ pygi instrument search Apple

Parameters
^^^^^^^^^^

Each ``object``/``action`` combination can have its own set of parameters. Whether these
parameters are mandatory or optional, and what set of parameters are available depends
on the ``object``/``action`` combination.
Use help functionality to find out more information about such parameters.

Getting help
------------

You can get help information about any command or subcommand by using ``--help`` or ``-h`` option.

List all available objects/commands::
  
    $ pygi -h
    usage: pygi [-h] [--format {json,text}] {instrument,positions,account} ...
    
    Command line utility to interact with IG Index trading platform
    
    positional arguments:
      {instrument,positions,account}
        instrument          Instruments
        positions           Manage positions
        account             Query account details
    
    optional arguments:
      -h, --help            show this help message and exit
      --format {json,text}  Output format type

List action commands for one specific object::
      
    $ pygi instrument -h
    usage: pygi instrument [-h] {get,search} ...
    
    positional arguments:
      {get,search}
        get         Get instrument details
        search      Search for instrument
    
    optional arguments:
      -h, --help    show this help message and exit

Show command specific parameters::
      
    $ pygi instrument search -h
    usage: pygi instrument search [-h] term
    
    positional arguments:
      term        Search term
    
    optional arguments:
      -h, --help  show this help message and exit
    
Examples
--------

List all open positions::

    $ pygi positions get
    Deal ID          IG Instrument       Market                        Size        Open      Latest         P/L
    XXAAAAXXXXXXXXX  UA.D.AAPL.DAILY.IP  Apple Inc (All Sessions)       0.1    13664.00    12500.00     -116.40
    XXAAAAXXXXXXXXX  UA.D.AAPL.DAILY.IP  Apple Inc (All Sessions)       0.1    12234.00    12500.00       26.60
    XXAAAAXXXXXXXXX  IX.D.FTSE.DAILY.IP  FTSE 100                       0.5     6873.60     7015.20       70.80
                                                                                          Total:         -19.00


Get account details in JSON format::

    $ pygi --format json account get
    {
        "accounts": {                                                                       
            "accounts": [                                                                   
                {              
                    "accountAlias": null,
                    "accountId": "XXXXX",   
                    "accountName": "CFD",
                    "accountType": "CFD",
                    "balance": {
                        "available": 0.0,
                        "balance": 0.0,
                        "deposit": 0.0,
                        "profitLoss": 0.0
                    },
                    "canTransferFrom": true,
                    "canTransferTo": true,
                    "currency": "GBP",
                    "preferred": false,
                    "status": "ENABLED"
                },
                {
                    "accountAlias": null,
                    "accountId": "XXXXX",
                    "accountName": "Spread bet", 
                    "accountType": "SPREADBET",
                    "balance": {
                        "available": 0.0,
                        "balance": 0.0,
                        "deposit": 0.0,
                        "profitLoss": 0.0
                    },
                    "canTransferFrom": true,
                    "canTransferTo": true,
                    "currency": "GBP",
                    "preferred": true,
                    "status": "ENABLED"
                }
            ]
        },
        "session": {
            "accountId": "XXXXX",
            "clientId": "000000000",
            "currency": "GBP",
            "lightstreamerEndpoint": "https://apd.marketdatasystems.com",
            "locale": "en_GB",
            "timezoneOffset": 1
        }
    }


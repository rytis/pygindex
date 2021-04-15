.. PyGIndex documentation master file, created by
   sphinx-quickstart on Wed Apr 14 13:21:14 2021.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

Welcome to PyGIndex documentation!
==================================

PyGIndex is a library and framework to access, interact and trade on IG Index platform.

User guide
----------

.. toctree::
   :maxdepth: 2

   installation	      

Examples
--------

Get session data:

.. code-block:: python

   from pygindex.client import IGClient

   c = IGClient()
   s = c.get_session_details()
   print(s)

Produces::

  {
    'clientId': 'XXXXXXXXX', 
    'accountId': 'XXXXX', 
    'timezoneOffset': 1, 
    'locale': 'en_GB', 
    'currency': 'GBP', 
    'lightstreamerEndpoint': 'https://apd.marketdatasystems.com'
  }

Get account details:
  
.. code-block:: python
   
    from pygindex.client import IGClient

    c = IGClient()
    s = c.get_accounts()
    print(s)

Produces::

    {
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
    }

API Reference
-------------

Information about specific function, class or method.

.. toctree::
   :maxdepth: 2

   api   


Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`

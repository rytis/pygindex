.. PyGIndex documentation master file, created by
   sphinx-quickstart on Wed Apr 14 13:21:14 2021.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

Welcome to PyGIndex documentation!
==================================

PyGIndex is a library and framework to access, interact and trade on IG Index platform.

Examples
--------

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

Installation
============

Python version
--------------

Recommended Python version is 3.9 and above.

Dependencies
------------

**PyGindex** depends on the following packages, that will be
automatically installed:

* `Requests`_ is used to interact with IG Index API services
  over HTTPS

.. _Requests: https://docs.python-requests.org/

Virtual environment
-------------------

Recommended way of installing **PyGIndex** is to use
Python virtual environment.

Python comes with :mod:`venv` module, which makes it
easy to start using virtual environments.

Create new environment
~~~~~~~~~~~~~~~~~~~~~~

In your project directory initialise new environment:

.. code-block:: sh

    $ mkdir new_project
    $ cd new_project
    $ python3 -m venv .venv

Activate the environment
~~~~~~~~~~~~~~~~~~~~~~~~

You need to activate the newly created environment before
you install **PyGIndex** and its dependencies:

.. code-block:: sh

   $ cd new_project
   $ source .venv/bin/activate

.. note::

   Once you're done with your work on the project code
   and want to switch to another environment, you need
   to de-activate it first:

   .. code-block:: sh

      $ deactivate

Install PyGIndex
----------------

In the active environment run the following command to
install **PyGIndex**:

.. code-block:: sh

   $ pip install pygindex -U

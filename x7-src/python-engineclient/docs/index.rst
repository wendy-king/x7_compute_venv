Python bindings to the X7 Engine API
==================================================

This is a client for X7 Engine API. There's :doc:`a Python API
<api>` (the :mod:`engineclient` module), and a :doc:`command-line script
<shell>` (installed as :program:`engine`). Each implements the entire
X7 Engine API.

You'll need an `X7 Engine` account, which you can get by using `engine-manage`.

.. seealso::

    You may want to read `Rackspace's API guide`__ (PDF) -- the first bit, at
    least -- to get an idea of the concepts. Rackspace is doing the cloud
    hosting thing a bit differently from Amazon, and if you get the concepts
    this library should make more sense.

    __ http://docs.rackspacecloud.com/servers/api/cs-devguide-latest.pdf

Contents:

.. toctree::
   :maxdepth: 2

   shell
   api
   ref/index
   releases

Contributing
============

Development takes place `on GitHub`__; please file bugs/pull requests there.

__ https://github.com/rackspace/python-engineclient

Run tests with ``python setup.py test``.

Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`


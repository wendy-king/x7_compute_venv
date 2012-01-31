..
      Copyright 2010-2011 United States Government as represented by the
      Administrator of the National Aeronautics and Space Administration. 
      All Rights Reserved.

      Licensed under the Apache License, Version 2.0 (the "License"); you may
      not use this file except in compliance with the License. You may obtain
      a copy of the License at

          http://www.apache.org/licenses/LICENSE-2.0

      Unless required by applicable law or agreed to in writing, software
      distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
      WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
      License for the specific language governing permissions and limitations
      under the License.

API Endpoint
============

Engine has a system for managing multiple APIs on different subdomains.
Currently there is support for the X7 API, as well as the Amazon EC2
API.

Common Components
-----------------

The :mod:`engine.api` Module
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
.. automodule:: engine.api
    :noindex:
    :members:
    :undoc-members:
    :show-inheritance:

The :mod:`engine.api.cloud` Module
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. automodule:: engine.api.cloud
    :noindex:
    :members:
    :undoc-members:
    :show-inheritance:

X7 API
-------------

The :mod:`x7` Module
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
.. automodule:: engine.api.x7
    :noindex:
    :members:
    :undoc-members:
    :show-inheritance:

The :mod:`auth` Module
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
.. automodule:: engine.api.x7.auth
    :noindex:
    :members:
    :undoc-members:
    :show-inheritance:

The :mod:`backup_schedules` Module
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
.. automodule:: engine.api.x7.backup_schedules
    :noindex:
    :members:
    :undoc-members:
    :show-inheritance:

The :mod:`faults` Module
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
.. automodule:: engine.api.x7.faults
    :noindex:
    :members:
    :undoc-members:
    :show-inheritance:

The :mod:`flavors` Module
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
.. automodule:: engine.api.x7.flavors
    :noindex:
    :members:
    :undoc-members:
    :show-inheritance:

The :mod:`images` Module
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
.. automodule:: engine.api.x7.images
    :noindex:
    :members:
    :undoc-members:
    :show-inheritance:

The :mod:`ratelimiting` Module
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
.. automodule:: engine.api.x7.ratelimiting
    :noindex:
    :members:
    :undoc-members:
    :show-inheritance:

The :mod:`servers` Module
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
.. automodule:: engine.api.x7.servers
    :noindex:
    :members:
    :undoc-members:
    :show-inheritance:

The :mod:`sharedipgroups` Module
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
.. automodule:: engine.api.x7.sharedipgroups
    :noindex:
    :members:
    :undoc-members:
    :show-inheritance:

EC2 API
-------

The :mod:`engine.api.ec2` Module
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. automodule:: engine.api.ec2
    :noindex:
    :members:
    :undoc-members:
    :show-inheritance:

The :mod:`admin` Module
~~~~~~~~~~~~~~~~~~~~~~~

.. automodule:: engine.api.ec2.admin
    :noindex:
    :members:
    :undoc-members:
    :show-inheritance:

The :mod:`apirequest` Module
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. automodule:: engine.api.ec2.apirequest
    :noindex:
    :members:
    :undoc-members:
    :show-inheritance:

The :mod:`cloud` Module
~~~~~~~~~~~~~~~~~~~~~~~

.. automodule:: engine.api.ec2.cloud
    :noindex:
    :members:
    :undoc-members:
    :show-inheritance:

The :mod:`images` Module
~~~~~~~~~~~~~~~~~~~~~~~~

.. automodule:: engine.api.ec2.images
    :noindex:
    :members:
    :undoc-members:
    :show-inheritance:

The :mod:`metadatarequesthandler` Module
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. automodule:: engine.api.ec2.metadatarequesthandler
    :noindex:
    :members:
    :undoc-members:
    :show-inheritance:

Tests
-----

The :mod:`api_unittest` Module
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. automodule:: engine.tests.api_unittest
    :noindex:
    :members:
    :undoc-members:
    :show-inheritance:

The :mod:`api_integration` Module
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. automodule:: engine.tests.api_integration
    :noindex:
    :members:
    :undoc-members:
    :show-inheritance:

The :mod:`cloud_unittest` Module
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. automodule:: engine.tests.cloud_unittest
    :noindex:
    :members:
    :undoc-members:
    :show-inheritance:

The :mod:`api.fakes` Module
~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. automodule:: engine.tests.api.fakes
    :noindex:
    :members:
    :undoc-members:
    :show-inheritance:

The :mod:`api.test_wsgi` Module
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. automodule:: engine.tests.api.test_wsgi
    :noindex:
    :members:
    :undoc-members:
    :show-inheritance:

The :mod:`test_api` Module
~~~~~~~~~~~~~~~~~~~~~~~~~~

.. automodule:: engine.tests.api.x7.test_api
    :noindex:
    :members:
    :undoc-members:
    :show-inheritance:

The :mod:`test_auth` Module
~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. automodule:: engine.tests.api.x7.test_auth
    :noindex:
    :members:
    :undoc-members:
    :show-inheritance:

The :mod:`test_faults` Module
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. automodule:: engine.tests.api.x7.test_faults
    :noindex:
    :members:
    :undoc-members:
    :show-inheritance:

The :mod:`test_flavors` Module
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. automodule:: engine.tests.api.x7.test_flavors
    :noindex:
    :members:
    :undoc-members:
    :show-inheritance:

The :mod:`test_images` Module
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. automodule:: engine.tests.api.x7.test_images
    :noindex:
    :members:
    :undoc-members:
    :show-inheritance:

The :mod:`test_ratelimiting` Module
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. automodule:: engine.tests.api.x7.test_ratelimiting
    :noindex:
    :members:
    :undoc-members:
    :show-inheritance:

The :mod:`test_servers` Module
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. automodule:: engine.tests.api.x7.test_servers
    :noindex:
    :members:
    :undoc-members:
    :show-inheritance:

The :mod:`test_sharedipgroups` Module
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. automodule:: engine.tests.api.x7.test_sharedipgroups
    :noindex:
    :members:
    :undoc-members:
    :show-inheritance:


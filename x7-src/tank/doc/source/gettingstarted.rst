..
      Copyright 2010 X7, LLC
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

Quick Guide to Getting Started with Tank
==========================================

Tank is a server that provides the following services:

* Ability to store and retrieve virtual machine images
* Ability to store and retrieve metadata about these virtual machine images
* FUTURE: Convert a virtual machine image from one format to another
* FUTURE: Help caching proxies such as Varnish or Squid cache machine images

Communication with Tank occurs via a REST-like HTTP interface.

However, Tank includes a :doc:`Client <client>` class that makes working with Tank
easy and straightforward.

In the Cactus release, there will be also command-line tools for
interacting with Tank.

Overview of Tank Architecture
-------------------------------

There are two main parts to Tank's architecture:

* Tank API server
* Tank Registry server(s)

Tank API Server
*****************

The API server is the main interface for Tank. It routes requests from
clients to registries of image metadata and to its **backend stores**, which
are the mechanisms by which Tank actually saves incoming virtual machine
images.

The backend stores that Tank can work with are as follows:

* **Chase**

  Chase is the highly-available object storage project in X7. More
  information can be found about Chase `here <http://chase.x7.org>`_.

* **Filesystem**

  The default backend that Tank uses to store virtual machine images
  is the filesystem backend. This simple backend writes image files to the
  local filesystem.

* **S3**

  This backend allows Tank to store virtual machine images in Amazon's
  S3 service.

* **HTTP**

  Tank can read virtual machine images that are available via
  HTTP somewhere on the Internet.  This store is **readonly**

Tank Registry Servers
***********************

Tank registry servers are servers that conform to the Tank Registry API.
Tank ships with a reference implementation of a registry server that
complies with this API (``tank-registry``).

For more details on Tank's architecture see :doc:`here <architecture>`. For
more information on what a Tank registry server is, see
:doc:`here <registries>`.

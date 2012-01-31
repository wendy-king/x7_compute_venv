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

Tank Architecture
===================

Tank is designed to be as adaptable as possible for various back-end storage
and registry database solutions. There is a main Tank API server
(the ``tank-api`` program) that serves as the communications hub between
various client programs, the registry of image metadata, and the storage
systems that actually contain the virtual machine image data.

From a birdseye perspective, one can visualize the Tank architectural model
like so:

.. graphviz::

  digraph birdseye {
    node [fontsize=10 fontname="Monospace"]
    a [label="Client A"]
    b [label="Client B"]
    c [label="Client C"]
    d [label="Tank API Server"]
    e [label="Registry Server"]
    f [label="Store Adapter"]
    g [label="S3 Store"]
    h [label="Chase Store"]
    i [label="Filesystem Store"]
    j [label="HTTP Store"]
    a -> d [dir=both]
    b -> d [dir=both]
    c -> d [dir=both]
    d -> e [dir=both]
    d -> f [dir=both]
    f -> g [dir=both]
    f -> h [dir=both]
    f -> i [dir=both]
    f -> j [dir=both]

  }

What is a Registry Server?
==========================

A registry server is any service that publishes image metadata that conforms
to the Tank Registry REST-ful API. Tank comes with a reference
implementation of a registry server called ``tank-registry``, but this is
only a reference implementation that uses a SQL database for its metdata
storage.

What is a Store?
================

A store is a Python class that inherits from ``tank.store.Backend`` and
conforms to that class' API for reading, writing, and deleting virtual
machine image data.

Tank currently ships with stores for S3, Chase, RBD, a simple filesystem store,
and a read-only HTTP(S) store.

Implementors are encouraged to create stores for other backends, including
other distributed storage systems like Sheepdog.

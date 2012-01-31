==========
tank-api
==========

---------------------------------------
Server for the Tank Image Service API
---------------------------------------

:Author: tank@lists.launchpad.net
:Date:   2010-11-16
:Copyright: X7 LLC
:Version: 0.1.2
:Manual section: 1
:Manual group: cloud computing

SYNOPSIS
========

  tank-api [options]

DESCRIPTION
===========

tank-api is a server daemon that serves the Tank API

OPTIONS
=======

  **General options**

  **-v, --verbose**
        Print more verbose output

  **--api_host=HOST**
        Address of host running ``tank-api``. Defaults to `0.0.0.0`.

  **--api_port=PORT**
        Port that ``tank-api`` listens on. Defaults to `9292`.

  **--default_store=STORE**
        The default backend store that Tank should use when storing virtual
        machine images. The default value is `filesystem`. Choices are any of
        `filesystem`, `chase`, or `s3`

  **--filesystem_store_datadir=DIR**
        The directory that the `filesystem` backend store should use to write
        virtual machine images. This directory should be writeable by the user
        running ``tank-api``

FILES
=====

None

SEE ALSO
========

* `X7 Tank <http://tank.x7.org>`__

BUGS
====

* Tank is sourced in Launchpad so you can view current bugs at `X7 Tank <http://tank.x7.org>`__

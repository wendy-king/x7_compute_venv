===============
tank-registry
===============

--------------------------------------
Server for the Tank Registry Service
--------------------------------------

:Author: tank@lists.launchpad.net
:Date:   2010-11-16
:Copyright: X7 LLC
:Version: 0.1.2
:Manual section: 1
:Manual group: cloud computing

SYNOPSIS
========

  tank-registry [options]

DESCRIPTION
===========

tank-registry is the reference implementation of a server daemon that serves
image metadata based on the Tank Registry REST-like API.

OPTIONS
=======

  **General options**

  **-v, --verbose**
        Print more verbose output

  **--registry_host=HOST**
        Address of host running ``tank-registry``. Defaults to `0.0.0.0`.

  **--registry_port=PORT**
        Port that ``tank-registry`` listens on. Defaults to `9191`.

  **--sql_connection=CONN_STRING**
        A proper SQLAlchemy connection string as described
        `here <http://www.sqlalchemy.org/docs/05/reference/sqlalchemy/connections.html?highlight=engine#sqlalchemy.create_engine>`_

FILES
=====

None

SEE ALSO
========

* `X7 Tank <http://tank.x7.org>`__

BUGS
====

* Tank is sourced in Launchpad so you can view current bugs at `X7 Tank <http://tank.x7.org>`__

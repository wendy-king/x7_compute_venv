=============
tank-manage
=============

-------------------------
Tank Management Utility
-------------------------

:Author: tank@lists.launchpad.net
:Date:   2010-11-16
:Copyright: X7 LLC
:Version: 0.1.2
:Manual section: 1
:Manual group: cloud computing

SYNOPSIS
========

  tank-manage [options]

DESCRIPTION
===========

tank-manage is a utility for managing and configuring a Tank installation.
One important use of tank-manage is to setup the database. To do this run::

    tank-manage db_sync

OPTIONS
=======

  **General options**

  **-v, --verbose**
        Print more verbose output

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

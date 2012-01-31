..
      Copyright 2011 X7, LLC
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

Controlling Tank Servers
==========================

This section describes the ways to start, stop, and reload Tank's server
programs.

Starting a server
-----------------

There are two ways to start a Tank server (either the API server or the
reference implementation registry server that ships with Tank):

* Manually calling the server program

* Using the ``tank-control`` server daemon wrapper program

We recommend using the second way.

Manually starting the server
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

The first is by directly calling the server program, passing in command-line
options and a single argument for a ``paste.deploy`` configuration file to
use when configuring the server application.

.. note::

  Tank ships with an ``etc/`` directory that contains sample ``paste.deploy``
  configuration files that you can copy to a standard configuation directory and
  adapt for your own uses. Specifically, bind_host must be set properly.

If you do `not` specifiy a configuration file on the command line, Tank will
do its best to locate a configuration file in one of the
following directories, stopping at the first config file it finds:

* ``$CWD``
* ``~/.tank``
* ``~/``
* ``/etc/tank``
* ``/etc``

The filename that is searched for depends on the server application name. So,
if you are starting up the API server, ``tank-api.conf`` is searched for,
otherwise ``tank-registry.conf``.

If no configuration file is found, you will see an error, like::

  $> tank-api
  ERROR: Unable to locate any configuration file. Cannot load application tank-api

Here is an example showing how you can manually start the ``tank-api`` server and ``tank-registry`` in a shell.::

  $ sudo tank-api tank-api.conf --debug &  
  jsuh@mc-ats1:~$ 2011-04-13 14:50:12    DEBUG [tank-api] ********************************************************************************
  2011-04-13 14:50:12    DEBUG [tank-api] Configuration options gathered from config file:
  2011-04-13 14:50:12    DEBUG [tank-api] /home/jsuh/tank-api.conf
  2011-04-13 14:50:12    DEBUG [tank-api] ================================================
  2011-04-13 14:50:12    DEBUG [tank-api] bind_host                      65.114.169.29
  2011-04-13 14:50:12    DEBUG [tank-api] bind_port                      9292
  2011-04-13 14:50:12    DEBUG [tank-api] debug                          True
  2011-04-13 14:50:12    DEBUG [tank-api] default_store                  file
  2011-04-13 14:50:12    DEBUG [tank-api] filesystem_store_datadir       /home/jsuh/images/
  2011-04-13 14:50:12    DEBUG [tank-api] registry_host                  65.114.169.29
  2011-04-13 14:50:12    DEBUG [tank-api] registry_port                  9191
  2011-04-13 14:50:12    DEBUG [tank-api] verbose                        False
  2011-04-13 14:50:12    DEBUG [tank-api] ********************************************************************************
  2011-04-13 14:50:12    DEBUG [routes.middleware] Initialized with method overriding = True, and path info altering = True
  2011-04-13 14:50:12    DEBUG [eventlet.wsgi.server] (21354) wsgi starting up on http://65.114.169.29:9292/

  $ sudo tank-registry tank-registry.conf &  
  jsuh@mc-ats1:~$ 2011-04-13 14:51:16     INFO [sqlalchemy.engine.base.Engine.0x...feac] PRAGMA table_info("images")
  2011-04-13 14:51:16     INFO [sqlalchemy.engine.base.Engine.0x...feac] ()
  2011-04-13 14:51:16    DEBUG [sqlalchemy.engine.base.Engine.0x...feac] Col ('cid', 'name', 'type', 'notnull', 'dflt_value', 'pk')
  2011-04-13 14:51:16    DEBUG [sqlalchemy.engine.base.Engine.0x...feac] Row (0, u'created_at', u'DATETIME', 1, None, 0)
  2011-04-13 14:51:16    DEBUG [sqlalchemy.engine.base.Engine.0x...feac] Row (1, u'updated_at', u'DATETIME', 0, None, 0)
  2011-04-13 14:51:16    DEBUG [sqlalchemy.engine.base.Engine.0x...feac] Row (2, u'deleted_at', u'DATETIME', 0, None, 0)
  2011-04-13 14:51:16    DEBUG [sqlalchemy.engine.base.Engine.0x...feac] Row (3, u'deleted', u'BOOLEAN', 1, None, 0)
  2011-04-13 14:51:16    DEBUG [sqlalchemy.engine.base.Engine.0x...feac] Row (4, u'id', u'INTEGER', 1, None, 1)
  2011-04-13 14:51:16    DEBUG [sqlalchemy.engine.base.Engine.0x...feac] Row (5, u'name', u'VARCHAR(255)', 0, None, 0)
  2011-04-13 14:51:16    DEBUG [sqlalchemy.engine.base.Engine.0x...feac] Row (6, u'disk_format', u'VARCHAR(20)', 0, None, 0)
  2011-04-13 14:51:16    DEBUG [sqlalchemy.engine.base.Engine.0x...feac] Row (7, u'container_format', u'VARCHAR(20)', 0, None, 0)
  2011-04-13 14:51:16    DEBUG [sqlalchemy.engine.base.Engine.0x...feac] Row (8, u'size', u'INTEGER', 0, None, 0)
  2011-04-13 14:51:16    DEBUG [sqlalchemy.engine.base.Engine.0x...feac] Row (9, u'status', u'VARCHAR(30)', 1, None, 0)
  2011-04-13 14:51:16    DEBUG [sqlalchemy.engine.base.Engine.0x...feac] Row (10, u'is_public', u'BOOLEAN', 1, None, 0)
  2011-04-13 14:51:16    DEBUG [sqlalchemy.engine.base.Engine.0x...feac] Row (11, u'location', u'TEXT', 0, None, 0)
  2011-04-13 14:51:16     INFO [sqlalchemy.engine.base.Engine.0x...feac] PRAGMA table_info("image_properties")
  2011-04-13 14:51:16     INFO [sqlalchemy.engine.base.Engine.0x...feac] ()
  2011-04-13 14:51:16    DEBUG [sqlalchemy.engine.base.Engine.0x...feac] Col ('cid', 'name', 'type', 'notnull', 'dflt_value', 'pk')
  2011-04-13 14:51:16    DEBUG [sqlalchemy.engine.base.Engine.0x...feac] Row (0, u'created_at', u'DATETIME', 1, None, 0)
  2011-04-13 14:51:16    DEBUG [sqlalchemy.engine.base.Engine.0x...feac] Row (1, u'updated_at', u'DATETIME', 0, None, 0)
  2011-04-13 14:51:16    DEBUG [sqlalchemy.engine.base.Engine.0x...feac] Row (2, u'deleted_at', u'DATETIME', 0, None, 0)
  2011-04-13 14:51:16    DEBUG [sqlalchemy.engine.base.Engine.0x...feac] Row (3, u'deleted', u'BOOLEAN', 1, None, 0)
  2011-04-13 14:51:16    DEBUG [sqlalchemy.engine.base.Engine.0x...feac] Row (4, u'id', u'INTEGER', 1, None, 1)
  2011-04-13 14:51:16    DEBUG [sqlalchemy.engine.base.Engine.0x...feac] Row (5, u'image_id', u'INTEGER', 1, None, 0)
  2011-04-13 14:51:16    DEBUG [sqlalchemy.engine.base.Engine.0x...feac] Row (6, u'key', u'VARCHAR(255)', 1, None, 0)
  2011-04-13 14:51:16    DEBUG [sqlalchemy.engine.base.Engine.0x...feac] Row (7, u'value', u'TEXT', 0, None, 0)

  $ ps aux | grep tank
  root     20009  0.7  0.1  12744  9148 pts/1    S    12:47   0:00 /usr/bin/python /usr/bin/tank-api tank-api.conf --debug
  root     20012  2.0  0.1  25188 13356 pts/1    S    12:47   0:00 /usr/bin/python /usr/bin/tank-registry tank-registry.conf
  jsuh     20017  0.0  0.0   3368   744 pts/1    S+   12:47   0:00 grep tank

Simply supply the configuration file as the first argument
(the ``etc/tank-api.conf`` and  ``etc/tank-registry.conf`` sample configuration
files were used in the above example) and then any common options
you want to use (``--debug`` was used above to show some of the debugging
output that the server shows when starting up. Call the server program
with ``--help`` to see all available options you can specify on the
command line.)

For more information on configuring the server via the ``paste.deploy``
configuration files, see the section entitled
:doc:`Configuring Tank servers <configuring>`

Note that the server `daemonizes` itself by using the standard
shell backgrounding indicator, ``&``, in the previous example. For most use cases, we recommend
using the ``tank-control`` server daemon wrapper for daemonizing. See below
for more details on daemonization with ``tank-control``.

Using the ``tank-control`` program to start the server
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

The second way to start up a Tank server is to use the ``tank-control``
program. ``tank-control`` is a wrapper script that allows the user to
start, stop, restart, and reload the other Tank server programs in
a fashion that is more conducive to automation and scripting.

Servers started via the ``tank-control`` program are always `daemonized`,
meaning that the server program process runs in the background.

To start a Tank server with ``tank-control``, simply call
``tank-control`` with a server and the word "start", followed by
any command-line options you wish to provide. Start the server with ``tank-control``
in the following way::

  $> sudo tank-control <SERVER> start [CONFPATH]

.. note::

  You must use the ``sudo`` program to run ``tank-control`` currently, as the
  pid files for the server programs are written to /var/run/tank/

Here is an example that shows how to start the ``tank-registry`` server
with the ``tank-control`` wrapper script. ::


  $ sudo tank-control api start tank-api.conf
  Starting tank-api with /home/jsuh/tank.conf

  $ sudo tank-control registry start tank-registry.conf
  Starting tank-registry with /home/jsuh/tank.conf

  $ ps aux | grep tank
  root     20038  4.0  0.1  12728  9116 ?        Ss   12:51   0:00 /usr/bin/python /usr/bin/tank-api /home/jsuh/tank-api.conf
  root     20039  6.0  0.1  25188 13356 ?        Ss   12:51   0:00 /usr/bin/python /usr/bin/tank-registry /home/jsuh/tank-registry.conf
  jsuh     20042  0.0  0.0   3368   744 pts/1    S+   12:51   0:00 grep tank

 
The same ``paste.deploy`` configuration files are used by ``tank-control``
to start the Tank server programs, and you can specify (as the example above
shows) a configuration file when starting the server.

Stopping a server
-----------------

If you started a Tank server manually and did not use the ``&`` backgrounding
function, simply send a terminate signal to the server process by typing
``Ctrl-C``

If you started the Tank server using the ``tank-control`` program, you can
use the ``tank-control`` program to stop it. Simply do the following::

  $> sudo tank-control <SERVER> stop

as this example shows::

  $> sudo tank-control registry stop
  Stopping tank-registry  pid: 17602  signal: 15

Restarting a server
-------------------

You can restart a server with the ``tank-control`` program, as demonstrated
here::

  $> sudo tank-control registry restart etc/tank-registry.conf
  Stopping tank-registry  pid: 17611  signal: 15
  Starting tank-registry with /home/jpipes/repos/tank/trunk/etc/tank-registry.conf

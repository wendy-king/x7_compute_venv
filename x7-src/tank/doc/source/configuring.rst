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

Configuring Tank
==================

Tank has a number of options that you can use to configure the Tank API
server, the Tank Registry server, and the various storage backends that
Tank can use to store images.

Most configuration is done via configuration files, with the Tank API
server and Tank Registry server using separate configuration files.

When starting up a Tank server, you can specify the configuration file to
use (see `the documentation on controller Tank servers <controllingservers>`_).
If you do **not** specify a configuration file, Tank will look in the following
directories for a configuration file, in order:

* ``~/.tank``
* ``~/``
* ``/etc/tank``
* ``/etc``

The Tank API server configuration file should be named ``tank-api.conf``.
Similarly, the Tank Registry server configuration file should be named
``tank-registry.conf``. If you installed Tank via your operating system's
package management system, it is likely that you will have sample
configuration files installed in ``/etc/tank``.

In addition to this documentation page, you can check the
``etc/tank-api.conf`` and ``etc/tank-registry.conf`` sample configuration
files distributed with Tank for example configuration files for each server
application with detailed comments on what each options does.

Common Configuration Options in Tank
--------------------------------------

Tank has a few command-line options that are common to all Tank programs:

* ``--verbose``

Optional. Default: ``False``

Can be specified on the command line and in configuration files.

Turns on the INFO level in logging and prints more verbose command-line
interface printouts.

* ``--debug``

Optional. Default: ``False``

Can be specified on the command line and in configuration files.

Turns on the DEBUG level in logging.

* ``--config-file=PATH``

Optional. Default: ``None``

Specified on the command line only.

Takes a path to a configuration file to use when running the program. If this
CLI option is not specified, then we check to see if the first argument is a
file. If it is, then we try to use that as the configuration file. If there is
no file or there were no arguments, we search for a configuration file in the
following order:

* ``~/.tank``
* ``~/``
* ``/etc/tank``
* ``/etc``

The filename that is searched for depends on the server application name. So,
if you are starting up the API server, ``tank-api.conf`` is searched for,
otherwise ``tank-registry.conf``.

Configuring Server Startup Options
----------------------------------

You can put the following options in the ``tank-api.conf`` and
``tank-registry.conf`` files, under the ``[DEFAULT]`` section. They enable
startup and binding behaviour for the API and registry servers, respectively.

* ``bind_host=ADDRESS``

The address of the host to bind to.

Optional. Default: ``0.0.0.0``

* ``bind_port=PORT``

The port the server should bind to.

Optional. Default: ``9191`` for the registry server, ``9292`` for the API server

* ``backlog=REQUESTS``

Number of backlog requests to configure the socket with.

Optional. Default: ``4096``

Configurating SSL Support
~~~~~~~~~~~~~~~~~~~~~~~~~

* ``cert_file=PATH``

Path to the the certificate file the server should use when binding to an
SSL-wrapped socket.

Optional. Default: not enabled.

* ``key_file=PATH``

Path to the the private key file the server should use when binding to an
SSL-wrapped socket.

Optional. Default: not enabled.

* ``registry_client_protocol=PROTOCOL``

If you run a secure Registry server, you need to set this value to ``https``
and also set ``registry_client_key_file`` and optionally
``registry_client_cert_file``.

Optional. Default: http

* ``registry_client_key_file=PATH``

The path to the key file to use in SSL connections to the
registry server, if any. Alternately, you may set the
``TANK_CLIENT_KEY_FILE`` environ variable to a filepath of the key file

Optional. Default: Not set.

* ``registry_client_cert_file=PATH``

Optional. Default: Not set.

The path to the cert file to use in SSL connections to the
registry server, if any. Alternately, you may set the
``TANK_CLIENT_CERT_FILE`` environ variable to a filepath of the cert file

* ``registry_client_ca_file=PATH``

Optional. Default: Not set.

The path to a Certifying Authority's cert file to use in SSL connections to the
registry server, if any. Alternately, you may set the
``TANK_CLIENT_CA_FILE`` environ variable to a filepath of the CA cert file

Configuring Logging in Tank
-----------------------------

There are a number of configuration options in Tank that control how Tank
servers log messages.

* ``--log-config=PATH``

Optional. Default: ``None``

Specified on the command line only.

Takes a path to a configuration file to use for configuring logging.

Logging Options Available Only in Configuration Files
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

You will want to place the different logging options in the **[DEFAULT]** section
in your application configuration file. As an example, you might do the following
for the API server, in a configuration file called ``etc/tank-api.conf``::

  [DEFAULT]
  log_file = /var/log/tank/api.log

* ``log_file``

The filepath of the file to use for logging messages from Tank's servers. If
missing, the default is to output messages to ``stdout``, so if you are running
Tank servers in a daemon mode (using ``tank-control``) you should make
sure that the ``log_file`` option is set appropriately.

* ``log_dir``

The filepath of the directory to use for log files. If not specified (the default)
the ``log_file`` is used as an absolute filepath.

* ``log_date_format``

The format string for timestamps in the log output.

Defaults to ``%Y-%m-%d %H:%M:%S``. See the
`logging module <http://docs.python.org/library/logging.html>`_ documentation for
more information on setting this format string.

* ``log_use_syslog``

Use syslog logging functionality.

Defaults to False.

Configuring Tank Storage Backends
-----------------------------------

There are a number of configuration options in Tank that control how Tank
stores disk images. These configuration options are specified in the
``tank-api.conf`` config file in the section ``[DEFAULT]``.

* ``default_store=STORE``

Optional. Default: ``file``

Can only be specified in configuration files.

Sets the storage backend to use by default when storing images in Tank.
Available options for this option are (``file``, ``chase``, ``s3``, or ``rbd``).

Configuring the Filesystem Storage Backend
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

* ``filesystem_store_datadir=PATH``

Optional. Default: ``/var/lib/tank/images/``

Can only be specified in configuration files.

`This option is specific to the filesystem storage backend.`

Sets the path where the filesystem storage backend write disk images. Note that
the filesystem storage backend will attempt to create this directory if it does
not exist. Ensure that the user that ``tank-api`` runs under has write
permissions to this directory.

Configuring the Chase Storage Backend
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

* ``chase_store_auth_address=URL``

Required when using the Chase storage backend.

Can only be specified in configuration files.

`This option is specific to the Chase storage backend.`

Sets the authentication URL supplied to Chase when making calls to its storage
system. For more information about the Chase authentication system, please
see the `Chase auth <http://chase.x7.org/overview_auth.html>`_ 
documentation and the
`overview of Chase authentication <http://docs.x7.org/x7-object-storage/admin/content/ch02s02.html>`_.

**IMPORTANT NOTE**: Chase authentication addresses use HTTPS by default. This
means that if you are running Chase with authentication over HTTP, you need
to set your ``chase_store_auth_address`` to the full URL, including the ``http://``.

* ``chase_store_user=USER``

Required when using the Chase storage backend.

Can only be specified in configuration files.

`This option is specific to the Chase storage backend.`

Sets the user to authenticate against the ``chase_store_auth_address`` with.

* ``chase_store_key=KEY``

Required when using the Chase storage backend.

Can only be specified in configuration files.

`This option is specific to the Chase storage backend.`

Sets the authentication key to authenticate against the
``chase_store_auth_address`` with for the user ``chase_store_user``.

* ``chase_store_container=CONTAINER``

Optional. Default: ``tank``

Can only be specified in configuration files.

`This option is specific to the Chase storage backend.`

Sets the name of the container to use for Tank images in Chase.

* ``chase_store_create_container_on_put``

Optional. Default: ``False``

Can only be specified in configuration files.

`This option is specific to the Chase storage backend.`

If true, Tank will attempt to create the container ``chase_store_container``
if it does not exist.

* ``chase_store_large_object_size=SIZE_IN_MB``

Optional. Default: ``5120``

Can only be specified in configuration files.

`This option is specific to the Chase storage backend.`

What size, in MB, should Tank start chunking image files
and do a large object manifest in Chase? By default, this is
the maximum object size in Chase, which is 5GB

* ``chase_store_large_object_chunk_size=SIZE_IN_MB``

Optional. Default: ``200``

Can only be specified in configuration files.

`This option is specific to the Chase storage backend.`

When doing a large object manifest, what size, in MB, should
Tank write chunks to Chase?  The default is 200MB.

Configuring the S3 Storage Backend
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

* ``s3_store_host=URL``

Required when using the S3 storage backend.

Can only be specified in configuration files.

`This option is specific to the S3 storage backend.`

Default: s3.amazonaws.com

Sets the main service URL supplied to S3 when making calls to its storage
system. For more information about the S3 authentication system, please
see the `S3 documentation <http://aws.amazon.com/documentation/s3/>`_ 

* ``s3_store_access_key=ACCESS_KEY``

Required when using the S3 storage backend.

Can only be specified in configuration files.

`This option is specific to the S3 storage backend.`

Sets the access key to authenticate against the ``s3_store_host`` with.

You should set this to your 20-character Amazon AWS access key.

* ``s3_store_secret_key=SECRET_KEY``

Required when using the S3 storage backend.

Can only be specified in configuration files.

`This option is specific to the S3 storage backend.`

Sets the secret key to authenticate against the
``s3_store_host`` with for the access key ``s3_store_access_key``.

You should set this to your 40-character Amazon AWS secret key.

* ``s3_store_bucket=BUCKET``

Required when using the S3 storage backend.

Can only be specified in configuration files.

`This option is specific to the S3 storage backend.`

Sets the name of the bucket to use for Tank images in S3.

Note that the namespace for S3 buckets is **global**, and
therefore you must use a name for the bucket that is unique. It
is recommended that you use a combination of your AWS access key,
**lowercased** with "tank".

For instance if your Amazon AWS access key is:

``ABCDEFGHIJKLMNOPQRST``

then make your bucket value be:

``abcdefghijklmnopqrsttank``

* ``s3_store_create_bucket_on_put``

Optional. Default: ``False``

Can only be specified in configuration files.

`This option is specific to the S3 storage backend.`

If true, Tank will attempt to create the bucket ``s3_store_bucket``
if it does not exist.

* ``s3_store_object_buffer_dir=PATH``

Optional. Default: ``the platform's default temporary directory``

Can only be specified in configuration files.

`This option is specific to the S3 storage backend.`

When sending images to S3, what directory should be
used to buffer the chunks? By default the platform's
temporary directory will be used.

Configuring the RBD Storage Backend
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

**Note**: the RBD storage backend requires the python bindings for
librados and librbd. These are in the python-ceph package on
Debian-based distributions.

* ``rbd_store_pool=POOL``

Optional. Default: ``rbd``

Can only be specified in configuration files.

`This option is specific to the RBD storage backend.`

Sets the RADOS pool in which images are stored.

* ``rbd_store_chunk_size=CHUNK_SIZE_MB``

Optional. Default: ``4``

Can only be specified in configuration files.

`This option is specific to the RBD storage backend.`

Images will be chunked into objects of this size (in megabytes).
For best performance, this should be a power of two.

* ``rbd_store_ceph_conf=PATH``

Optional. Default: ``/etc/ceph/ceph.conf``, ``~/.ceph/config``, and ``./ceph.conf``

Can only be specified in configuration files.

`This option is specific to the RBD storage backend.`

Sets the Ceph configuration file to use.

* ``rbd_store_user=NAME``

Optional. Default: ``admin``

Can only be specified in configuration files.

`This option is specific to the RBD storage backend.`

Sets the RADOS user to authenticate as. This is only needed
when `RADOS authentication <http://ceph.newdream.net/wiki/Cephx>`_
is `enabled. <http://ceph.newdream.net/wiki/Cluster_configuration#Cephx_auth>`_

A keyring must be set for this user in the Ceph
configuration file, e.g. with a user ``tank``::

  [client.tank]
  keyring=/etc/tank/rbd.keyring

To set up a user named ``tank`` with minimal permissions, using a pool called
``images``, run::

  rados mkpool images
  ceph-authtool --create-keyring /etc/tank/rbd.keyring
  ceph-authtool --gen-key --name client.tank --cap mon 'allow r' --cap osd 'allow rwx pool=images' /etc/tank/rbd.keyring
  ceph auth add client.tank -i /etc/tank/rbd.keyring

Configuring the Image Cache
---------------------------

Tank API servers can be configured to have a local image cache. Caching of
image files is transparent and happens using a piece of middleware that can
optionally be placed in the server application pipeline.

Enabling the Image Cache Middleware
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

To enable the image cache middleware, you would insert the cache middleware
into your application pipeline **after** the appropriate context middleware.

The cache middleware should be in your ``tank-api.conf`` in a section titled
``[filter:cache]``. It should look like this::

  [filter:cache]
  paste.filter_factory = tank.common.wsgi:filter_factory
  tank.filter_factory = tank.api.middleware.cache:CacheFilter


For example, suppose your application pipeline in the ``tank-api.conf`` file
looked like so::

  [pipeline:tank-api]
  pipeline = versionnegotiation context apiv1app

In the above application pipeline, you would add the cache middleware after the
context middleware, like so::

  [pipeline:tank-api]
  pipeline = versionnegotiation context cache apiv1app

And that would give you a transparent image cache on the API server.

Configuration Options Affecting the Image Cache
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

One main configuration file option affects the image cache.

 * ``image_cache_dir=PATH``

Required when image cache middleware is enabled.

Default: ``/var/lib/tank/image-cache``

This is the base directory the image cache can write files to.
Make sure the directory is writeable by the user running the
``tank-api`` server

 * ``image_cache_driver=DRIVER``

Optional. Choice of ``sqlite`` or ``xattr``

Default: ``sqlite``

The default ``sqlite`` cache driver has no special dependencies, other
than the ``python-sqlite3`` library, which is installed on virtually
all operating systems with modern versions of Python. It stores
information about the cached files in a SQLite database.

The ``xattr`` cache driver required the ``python-xattr>=0.6.0`` library
and requires that the filesystem containing ``image_cache_dir`` have
access times tracked for all files (in other words, the noatime option
CANNOT be set for that filesystem). In addition, ``user_xattr`` must be
set on the filesystem's description line in fstab. Because of these
requirements, the ``xattr`` cache driver is not available on Windows.

 * ``image_cache_sqlite_db=DB_FILE``

Optional.

Default: ``cache.db``

When using the ``sqlite`` cache driver, you can set the name of the database
that will be used to store the cached images information. The database
is always contained in the ``image_cache_dir``.

 * ``image_cache_max_size=SIZE``

Optional.

Default: ``10737418240`` (10 GB)

Size, in bytes, that the image cache should be constrained to. Images files
are cached automatically in the local image cache, even if the writing of that
image file would put the total cache size over this size. The
``tank-cache-pruner`` executable is what prunes the image cache to be equal
to or less than this value. The ``tank-cache-pruner`` executable is designed
to be run via cron on a regular basis. See more about this executable in
`Controlling the Growth of the Image Cache`

Configuring the Tank Registry
-------------------------------

Tank ships with a default, reference implementation registry server. There
are a number of configuration options in Tank that control how this registry
server operates. These configuration options are specified in the
``tank-registry.conf`` config file in the section ``[DEFAULT]``.

* ``sql_connection=CONNECTION_STRING`` (``--sql-connection`` when specified
  on command line)

Optional. Default: ``None``

Can be specified in configuration files. Can also be specified on the
command-line for the ``tank-manage`` program.

Sets the SQLAlchemy connection string to use when connecting to the registry
database. Please see the documentation for
`SQLAlchemy connection strings <http://www.sqlalchemy.org/docs/05/reference/sqlalchemy/connections.html>`_
online.

* ``sql_timeout=SECONDS``
  on command line)

Optional. Default: ``3600``

Can only be specified in configuration files.

Sets the number of seconds after which SQLAlchemy should reconnect to the
datastore if no activity has been made on the connection.

Configuring Notifications
-------------------------

Tank can optionally generate notifications to be logged or sent to
a RabbitMQ queue. The configuration options are specified in the
``tank-api.conf`` config file in the section ``[DEFAULT]``.

* ``notifier_strategy``

Optional. Default: ``noop``

Sets the strategy used for notifications. Options are ``logging``,
``rabbit`` and ``noop``.
For more information :doc:`Tank notifications <notifications>`

* ``rabbit_host``

Optional. Default: ``localhost``

Host to connect to when using ``rabbit`` strategy.

* ``rabbit_port``

Optional. Default: ``5672``

Port to connect to when using ``rabbit`` strategy.

* ``rabbit_use_ssl``

Optional. Default: ``false``

Boolean to use SSL for connecting when using ``rabbit`` strategy.

* ``rabbit_userid``

Optional. Default: ``guest``

Userid to use for connection when using ``rabbit`` strategy.

* ``rabbit_password``

Optional. Default: ``guest``

Password to use for connection when using ``rabbit`` strategy.

* ``rabbit_virtual_host``

Optional. Default: ``/``

Virtual host to use for connection when using ``rabbit`` strategy.

* ``rabbit_notification_exchange``

Optional. Default: ``tank``

Exchange name to use for connection when using ``rabbit`` strategy.

* ``rabbit_notification_topic``

Optional. Default: ``tank_notifications``

Topic to use for connection when using ``rabbit`` strategy.

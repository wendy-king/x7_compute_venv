The :mod:`engineclient` Python API
==================================

.. module:: engineclient
   :synopsis: A client for the X7 Engine API.

.. currentmodule:: engineclient

Usage
-----

First create an instance of :class:`X7` with your credentials::

    >>> from engineclient import X7
    >>> engine = X7(USERNAME, PASSWORD, AUTH_URL)

Then call methods on the :class:`X7` object:

.. class:: X7

    .. attribute:: backup_schedules

        A :class:`BackupScheduleManager` -- manage automatic backup images.

    .. attribute:: flavors

        A :class:`FlavorManager` -- query available "flavors" (hardware
        configurations).

    .. attribute:: images

        An :class:`ImageManager` -- query and create server disk images.

    .. attribute:: ipgroups

        A :class:`IPGroupManager` -- manage shared public IP addresses.

    .. attribute:: servers

        A :class:`ServerManager` -- start, stop, and manage virtual machines.

    .. automethod:: authenticate

For example::

    >>> engine.servers.list()
    [<Server: buildslave-ubuntu-9.10>]

    >>> engine.flavors.list()
    [<Flavor: 256 server>,
     <Flavor: 512 server>,
     <Flavor: 1GB server>,
     <Flavor: 2GB server>,
     <Flavor: 4GB server>,
     <Flavor: 8GB server>,
     <Flavor: 15.5GB server>]

    >>> fl = engine.flavors.find(ram=512)
    >>> engine.servers.create("my-server", flavor=fl)
    <Server: my-server>

For more information, see the reference:

.. toctree::
   :maxdepth: 2

   ref/index

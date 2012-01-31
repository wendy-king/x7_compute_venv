===========
engine-manage
===========

------------------------------------------------------
control and manage cloud computer instances and images
------------------------------------------------------

:Author: x7@lists.launchpad.net
:Date:   2010-11-16
:Copyright: X7 LLC
:Version: 0.1
:Manual section: 1
:Manual group: cloud computing

SYNOPSIS
========

  engine-manage <category> <action> [<args>]

DESCRIPTION
===========

engine-manage controls cloud computing instances by managing engine users, engine projects, engine roles, shell selection, vpn connections, and floating IP address configuration. More information about X7 Engine is at http://engine.x7.org.

OPTIONS
=======

The standard pattern for executing a engine-manage command is:
``engine-manage <category> <command> [<args>]``

For example, to obtain a list of all projects:
``engine-manage project list``

Run without arguments to see a list of available command categories:
``engine-manage``

Categories are user, project, role, shell, vpn, and floating. Detailed descriptions are below.

You can also run with a category argument such as user to see a list of all commands in that category:
``engine-manage user``

These sections describe the available categories and arguments for engine-manage.

Engine Db
~~~~~~~

``engine-manage db version``

    Print the current database version.

``engine-manage db sync``

    Sync the database up to the most recent version. This is the standard way to create the db as well.

Engine User
~~~~~~~~~

``engine-manage user admin <username>``

    Create an admin user with the name <username>.

``engine-manage user create <username>``

    Create a normal user with the name <username>.

``engine-manage user delete <username>``

    Delete the user with the name <username>.

``engine-manage user exports <username>``

    Outputs a list of access key and secret keys for user to the screen

``engine-manage user list``

    Outputs a list of all the user names to the screen.

``engine-manage user modify <accesskey> <secretkey> <admin?T/F>``

    Updates the indicated user keys, indicating with T or F if the user is an admin user. Leave any argument blank if you do not want to update it.

Engine Project
~~~~~~~~~~~~

``engine-manage project add <projectname>``

    Add a engine project with the name <projectname> to the database.

``engine-manage project create <projectname>``

    Create a new engine project with the name <projectname> (you still need to do engine-manage project add <projectname> to add it to the database).

``engine-manage project delete <projectname>``

    Delete a engine project with the name <projectname>.

``engine-manage project environment <projectname> <username>``

    Exports environment variables for the named project to a file named enginerc.

``engine-manage project list``

    Outputs a list of all the projects to the screen.

``engine-manage project quota <projectname>``

    Outputs the size and specs of the project's instances including gigabytes, instances, floating IPs, volumes, and cores.

``engine-manage project remove <projectname>``

    Deletes the project with the name <projectname>.

``engine-manage project zipfile``

    Compresses all related files for a created project into a zip file engine.zip.

Engine Role
~~~~~~~~~

engine-manage role <action> [<argument>]
``engine-manage role add <username> <rolename> <(optional) projectname>``

    Add a user to either a global or project-based role with the indicated <rolename> assigned to the named user. Role names can be one of the following five roles: cloudadmin, itsec, sysadmin, netadmin, developer. If you add the project name as the last argument then the role is assigned just for that project, otherwise the user is assigned the named role for all projects.

``engine-manage role has <username> <projectname>``
    Checks the user or project and responds with True if the user has a global role with a particular project.

``engine-manage role remove <username> <rolename>``
    Remove the indicated role from the user.

Engine Shell
~~~~~~~~~~

``engine-manage shell bpython``

    Starts a new bpython shell.

``engine-manage shell ipython``

    Starts a new ipython shell.

``engine-manage shell python``

    Starts a new python shell.

``engine-manage shell run``

    Starts a new shell using python.

``engine-manage shell script <path/scriptname>``

    Runs the named script from the specified path with flags set.

Engine VPN
~~~~~~~~

``engine-manage vpn list``

    Displays a list of projects, their IP prot numbers, and what state they're in.

``engine-manage vpn run <projectname>``

    Starts the VPN for the named project.

``engine-manage vpn spawn``

    Runs all VPNs.

Engine Floating IPs
~~~~~~~~~~~~~~~~~

``engine-manage floating create <host> <ip_range>``

    Creates floating IP addresses for the named host by the given range.

``engine-manage floating delete <ip_range>``

    Deletes floating IP addresses in the range given.

``engine-manage floating list``

    Displays a list of all floating IP addresses.

Engine Flavor
~~~~~~~~~~~

``engine-manage flavor list``

    Outputs a list of all active flavors to the screen.

``engine-manage flavor list --all``

    Outputs a list of all flavors (active and inactive) to the screen.

``engine-manage flavor create <name> <memory> <vCPU> <local_storage> <flavorID> <(optional) swap> <(optional) RXTX Quota> <(optional) RXTX Cap>``

    creates a flavor with the following positional arguments:
     * memory (expressed in megabytes)
     * vcpu(s) (integer)
     * local storage (expressed in gigabytes)
     * flavorid (unique integer)
     * swap space (expressed in megabytes, defaults to zero, optional)
     * RXTX quotas (expressed in gigabytes, defaults to zero, optional)
     * RXTX cap (expressed in gigabytes, defaults to zero, optional)

``engine-manage flavor delete <name>``

    Delete the flavor with the name <name>. This marks the flavor as inactive and cannot be launched. However, the record stays in the database for archival and billing purposes.

``engine-manage flavor delete <name> --purge``

    Purges the flavor with the name <name>. This removes this flavor from the database.

Engine Instance_type
~~~~~~~~~~~~~~~~~~

The instance_type command is provided as an alias for the flavor command. All the same subcommands and arguments from engine-manage flavor can be used.

Engine Images
~~~~~~~~~~~

``engine-manage image image_register <path> <owner>``

    Registers an image with the image service.

``engine-manage image kernel_register <path> <owner>``

    Registers a kernel with the image service.

``engine-manage image ramdisk_register <path> <owner>``

    Registers a ramdisk with the image service.

``engine-manage image all_register <image_path> <kernel_path> <ramdisk_path> <owner>``

    Registers an image kernel and ramdisk with the image service.

``engine-manage image convert <directory>``

    Converts all images in directory from the old (Bexar) format to the new format.

Engine VM
~~~~~~~~~~~

``engine-manage vm list [host]``
    Show a list of all instances. Accepts optional hostname (to show only instances on specific host).

``engine-manage live-migration <ec2_id> <destination host name>``
    Live migrate instance from current host to destination host. Requires instance id (which comes from euca-describe-instance) and destination host name (which can be found from engine-manage service list).


FILES
========

The engine-manage.conf file contains configuration information in the form of python-gflags.

SEE ALSO
========

* `X7 Engine <http://engine.x7.org>`__
* `X7 Chase <http://chase.x7.org>`__

BUGS
====

* Engine is sourced in Launchpad so you can view current bugs at `X7 Engine <http://engine.x7.org>`__




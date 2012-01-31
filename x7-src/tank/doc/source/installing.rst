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

Installing Tank
=================

Installing from packages
~~~~~~~~~~~~~~~~~~~~~~~~

To install the latest released version of Tank,
follow the following instructions.

Debian, Ubuntu
##############

1. Add the Tank PPA to your sources.lst::

   $> sudo add-apt-repository ppa:tank-core/trunk
   $> sudo apt-get update

2. Install Tank::

   $> sudo apt-get install tank

Red Hat, Fedora
###############

Only RHEL 6, Fedora 15, and newer releases have the necessary
components packaged.
On RHEL 6, enable the EPEL repository.

Install Tank::

   $ su -
   # yum install x7-tank

Mac OSX
#######

.. todo:: No idea how to do install on Mac OSX. Somebody with a Mac should complete this section

Installing from source tarballs
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

To install the latest version of Tank from the Launchpad Bazaar repositories,
following the following instructions.

1. Grab the source tarball from `Launchpad <http://launchpad.net/tank/+download>`_

2. Untar the source tarball::

   $> tar -xzf <FILE>

3. Change into the package directory and build/install::

   $> cd tank-<RELEASE>
   $> sudo python setup.py install

Installing from Git
~~~~~~~~~~~~~~~~~~~

To install the latest version of Tank from the GitHub Git repositories,
following the following instructions.

Debian, Ubuntu
##############

1. Install Git and build dependencies::

   $> sudo apt-get install git
   $> sudo apt-get build-dep tank

.. note::

   If you want to build the Tank documentation locally, you will also want
   to install the python-sphinx package

2. Clone Tank's trunk branch from GitHub::
   
   $> git clone git://github.com/x7/tank
   $> cd tank

3. Install Tank::
   
   $> sudo python setup.py install

Red Hat, Fedora
###############

On Fedora, most developers and essentially all users install packages.
Instructions below are not commonly used, and even then typically in a
throw-away VM.

Since normal build dependencies are resolved by mechanisms of RPM,
there is no one-line command to install everything needed by
the source repository in git. One common way to discover the dependencies
is to search for *BuildRequires:* in the specfile of x7-tank
for the appropriate distro.

In case of Fedora 16, for example, do this::

   $ su -
   # yum install git
   # yum install python2-devel python-setuptools python-distutils-extra
   # yum install python-webob python-eventlet python-boto
   # yum install python-virtualenv

Build Tank::

   $ python setup.py build

If any missing modules crop up, install them with yum, then retry the build.

.. note::

   If you want to build the Tank documentation, you will also want
   to install the packages python-sphinx and graphviz, then run
   "python setup.py build_sphinx". Due to required features of
   python-sphinx 1.0 or better, documentation can only be built
   on Fedora 15 or later.

Test the build::

   $ ./run_tests.sh -s

Once Tank is built and tested, install it::

   $ su -
   # python setup.py install

Mac OSX
#######

.. todo:: No idea how to do install on Mac OSX. Somebody with a Mac should complete this section

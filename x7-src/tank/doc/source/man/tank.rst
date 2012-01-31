======
tank
======

-----------------------------
Tank command line interface
-----------------------------

:Author: tank@lists.launchpad.net
:Date:   2012-01-03
:Copyright: X7 LLC
:Version: 2012.1-dev
:Manual section: 1
:Manual group: cloud computing


SYNOPSIS
========

  tank <command> [options] [args]


COMMANDS
========

  **help <command>**
        Output help for one of the commands below

  **add**
        Adds a new image to Tank

  **update**
        Updates an image's metadata in Tank

  **delete**
        Deletes an image from Tank

  **index**
        Return brief information about images in Tank

  **details**
        Return detailed information about images in Tank

  **show**
        Show detailed information about an image in Tank

  **clear**
        Removes all images and metadata from Tank


MEMBER COMMANDS
===============

  **image-members**
        List members an image is shared with

  **member-images**
        List images shared with a member

  **member-add**
        Grants a member access to an image

  **member-delete**
        Revokes a member's access to an image

  **members-replace**
        Replaces all membership for an image


OPTIONS
=======

  **--version**
        show program's version number and exit

  **-h, --help**
        show this help message and exit

  **-v, --verbose**
        Print more verbose output
 
  **-d, --debug**
        Print more verbose output
 
  **-H ADDRESS, --host=ADDRESS**
        Address of Tank API host. Default: 0.0.0.0

  **-p PORT, --port=PORT**
        Port the Tank API host listens on. Default: 9292

  **-U URL, --url=URL**
        URL of Tank service. This option can be used to specify the hostname,
        port and protocol (http/https) of the tank server, for example 
        -U https://localhost:9292/v1 
        Default: None

  **-A TOKEN, --auth_token=TOKEN**
        Authentication token to use to identify the client to the tank server

  **--limit=LIMIT**
        Page size to use while requesting image metadata

  **--marker=MARKER**
        Image index after which to begin pagination

  **--sort_key=KEY**
        Sort results by this image attribute.

  **--sort_dir=[desc|asc]**
        Sort results in this direction.

  **-f, --force**
        Prevent select actions from requesting user confirmation

  **--dry-run**
        Don't actually execute the command, just print output showing what 
        WOULD happen.

  **--can-share**
        Allow member to further share image.


SEE ALSO
========

* `X7 Tank <http://tank.x7.org>`__

BUGS
====

* Tank is sourced in Launchpad so you can view current bugs at `X7 Tank <http://tank.x7.org>`__

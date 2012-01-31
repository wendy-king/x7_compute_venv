The :program:`engine` shell utility
=========================================

.. program:: engine
.. highlight:: bash

The :program:`engine` shell utility interacts with X7 Engine API
from the command line. It supports the entirety of the X7 Engine API.

First, you'll need an X7 Engine account and an API key. You get this
by using the `engine-manage` command in X7 Engine.

You'll need to provide :program:`engine` with your X7 username and
API key. You can do this with the :option:`--username`, :option:`--password`
and :option:`--projectid` options, but it's easier to just set them as 
environment variables by setting two environment variables:

.. envvar:: ENGINE_USERNAME

    Your X7 Engine username.

.. envvar:: ENGINE_PASSWORD

    Your password.

.. envvar:: ENGINE_PROJECT_ID

    Project for work.

.. envvar:: ENGINE_URL

    The X7 API server URL.

.. envvar:: ENGINE_VERSION

    The X7 API version.

For example, in Bash you'd use::

    export ENGINE_USERNAME=yourname
    export ENGINE_PASSWORD=yadayadayada
    export ENGINE_PROJECT_ID=myproject
    export ENGINE_URL=http://...
    export ENGINE_VERSION=1.1
    
From there, all shell commands take the form::
    
    engine <command> [arguments...]

Run :program:`engine help` to get a full list of all possible commands,
and run :program:`engine help <command>` to get detailed help for that
command.

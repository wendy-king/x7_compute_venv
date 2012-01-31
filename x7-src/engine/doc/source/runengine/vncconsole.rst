..
      Copyright 2010-2011 United States Government as represented by the
      Administrator of the National Aeronautics and Space Administration.
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

Getting Started with the VNC Proxy
==================================

The VNC Proxy is an X7 component that allows users of Engine to access
their instances through a websocket enabled browser (like Google Chrome).

A VNC Connection works like so:

* User connects over an api and gets a url like http://ip:port/?token=xyz
* User pastes url in browser
* Browser connects to VNC Proxy though a websocket enabled client like noVNC
* VNC Proxy authorizes users token, maps the token to a host and port of an
  instance's VNC server
* VNC Proxy initiates connection to VNC server, and continues proxying until
  the session ends


Configuring the VNC Proxy
-------------------------
engine-vncproxy requires a websocket enabled html client to work properly.  At
this time, the only tested client is a slightly modified fork of noVNC, which
you can at find http://github.com/x7/noVNC.git

.. todo:: add instruction for installing from package

noVNC must be in the location specified by --vncproxy_wwwroot, which defaults
to /var/lib/engine/noVNC.  engine-vncproxy will fail to launch until this code
is properly installed.

By default, engine-vncproxy binds 0.0.0.0:6080.  This can be configured with:

* :option:`--vncproxy_port=[port]`
* :option:`--vncproxy_host=[host]`

It also binds a separate Flash socket policy listener on 0.0.0.0:843.  This
can be configured with:

* :option:`--vncproxy_flash_socket_policy_port=[port]`
* :option:`--vncproxy_flash_socket_policy_host=[host]`


Enabling VNC Consoles in Engine
-----------------------------
At the moment, VNC support is supported only when using libvirt.  To enable VNC
Console, configure the following flags:

* :option:`--vnc_console_proxy_url=http://[proxy_host]:[proxy_port]` -
  proxy_port defaults to 6080.  This url must point to engine-vncproxy
* :option:`--vnc_enabled=[True|False]` - defaults to True. If this flag is
  not set your instances will launch without vnc support.


Getting an instance's VNC Console
---------------------------------
You can access an instance's VNC Console url in the following methods:

* Using the direct api:
  eg: '``stack --user=admin --project=admin compute get_vnc_console instance_id=1``'
* Support for Dashboard, and the X7 API will be forthcoming


Accessing VNC Consoles without a web browser
--------------------------------------------
At the moment, VNC Consoles are only supported through the web browser, but
more general VNC support is in the works.

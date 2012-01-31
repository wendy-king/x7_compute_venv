# vim: tabstop=4 shiftwidth=4 softtabstop=4

# Copyright (c) 2011 X7, LLC.
# All Rights Reserved.
#
#    Licensed under the Apache License, Version 2.0 (the "License"); you may
#    not use this file except in compliance with the License. You may obtain
#    a copy of the License at
#
#         http://www.apache.org/licenses/LICENSE-2.0
#
#    Unless required by applicable law or agreed to in writing, software
#    distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
#    WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
#    License for the specific language governing permissions and limitations
#    under the License.


from engine.rootwrap.filters import CommandFilter, DnsmasqFilter

filters = [
    # engine/network/linux_net.py: 'ip', 'addr', 'add', str(floating_ip)+'/32'i..
    # engine/network/linux_net.py: 'ip', 'addr', 'del', str(floating_ip)+'/32'..
    # engine/network/linux_net.py: 'ip', 'addr', 'add', '169.254.169.254/32',..
    # engine/network/linux_net.py: 'ip', 'addr', 'show', 'dev', dev, 'scope',..
    # engine/network/linux_net.py: 'ip', 'addr', 'del/add', ip_params, dev)
    # engine/network/linux_net.py: 'ip', 'addr', 'del', params, fields[-1]
    # engine/network/linux_net.py: 'ip', 'addr', 'add', params, bridge
    # engine/network/linux_net.py: 'ip', '-f', 'inet6', 'addr', 'change', ..
    # engine/network/linux_net.py: 'ip', 'link', 'set', 'dev', dev, 'promisc',..
    # engine/network/linux_net.py: 'ip', 'link', 'add', 'link', bridge_if ...
    # engine/network/linux_net.py: 'ip', 'link', 'set', interface, "address",..
    # engine/network/linux_net.py: 'ip', 'link', 'set', interface, 'up'
    # engine/network/linux_net.py: 'ip', 'link', 'set', bridge, 'up'
    # engine/network/linux_net.py: 'ip', 'addr', 'show', 'dev', interface, ..
    # engine/network/linux_net.py: 'ip', 'link', 'set', dev, "address", ..
    # engine/network/linux_net.py: 'ip', 'link', 'set', dev, 'up'
    CommandFilter("/sbin/ip", "root"),

    # engine/network/linux_net.py: 'ip[6]tables-save' % (cmd,), '-t', ...
    CommandFilter("/sbin/iptables-save", "root"),
    CommandFilter("/sbin/ip6tables-save", "root"),

    # engine/network/linux_net.py: 'ip[6]tables-restore' % (cmd,)
    CommandFilter("/sbin/iptables-restore", "root"),
    CommandFilter("/sbin/ip6tables-restore", "root"),

    # engine/network/linux_net.py: 'arping', '-U', floating_ip, '-A', '-I', ...
    # engine/network/linux_net.py: 'arping', '-U', network_ref['dhcp_server'],..
    CommandFilter("/usr/bin/arping", "root"),

    # engine/network/linux_net.py: 'route', '-n'
    # engine/network/linux_net.py: 'route', 'del', 'default', 'gw'
    # engine/network/linux_net.py: 'route', 'add', 'default', 'gw'
    # engine/network/linux_net.py: 'route', '-n'
    # engine/network/linux_net.py: 'route', 'del', 'default', 'gw', old_gw, ..
    # engine/network/linux_net.py: 'route', 'add', 'default', 'gw', old_gateway
    CommandFilter("/sbin/route", "root"),

    # engine/network/linux_net.py: 'dhcp_release', dev, address, mac_address
    CommandFilter("/usr/bin/dhcp_release", "root"),

    # engine/network/linux_net.py: 'kill', '-9', pid
    # engine/network/linux_net.py: 'kill', '-HUP', pid
    # engine/network/linux_net.py: 'kill', pid
    CommandFilter("/bin/kill", "root"),

    # engine/network/linux_net.py: dnsmasq call
    DnsmasqFilter("/usr/sbin/dnsmasq", "root"),

    # engine/network/linux_net.py: 'radvd', '-C', '%s' % _ra_file(dev, 'conf'),..
    CommandFilter("/usr/sbin/radvd", "root"),

    # engine/network/linux_net.py: 'brctl', 'addbr', bridge
    # engine/network/linux_net.py: 'brctl', 'setfd', bridge, 0
    # engine/network/linux_net.py: 'brctl', 'stp', bridge, 'off'
    # engine/network/linux_net.py: 'brctl', 'addif', bridge, interface
    CommandFilter("/sbin/brctl", "root"),
    CommandFilter("/usr/sbin/brctl", "root"),

    # engine/network/linux_net.py: 'ovs-vsctl', ....
    CommandFilter("/usr/bin/ovs-vsctl", "root"),
    ]

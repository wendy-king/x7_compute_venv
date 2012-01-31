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
    # engine/virt/disk/mount.py: 'kpartx', '-a', device
    # engine/virt/disk/mount.py: 'kpartx', '-d', device
    CommandFilter("/sbin/kpartx", "root"),

    # engine/virt/disk/mount.py: 'tune2fs', '-c', 0, '-i', 0, mapped_device
    # engine/virt/xenapi/vm_utils.py: "tune2fs", "-O ^has_journal", part_path
    # engine/virt/xenapi/vm_utils.py: "tune2fs", "-j", partition_path
    CommandFilter("/sbin/tune2fs", "root"),

    # engine/virt/disk/mount.py: 'mount', mapped_device, mount_dir
    # engine/virt/xenapi/vm_utils.py: 'mount', '-t', 'ext2,ext3,ext4,reiserfs'..
    CommandFilter("/bin/mount", "root"),

    # engine/virt/disk/mount.py: 'umount', mapped_device
    # engine/virt/xenapi/vm_utils.py: 'umount', dev_path
    CommandFilter("/bin/umount", "root"),

    # engine/virt/disk/nbd.py: 'qemu-nbd', '-c', device, image
    # engine/virt/disk/nbd.py: 'qemu-nbd', '-d', device
    CommandFilter("/usr/bin/qemu-nbd", "root"),

    # engine/virt/disk/loop.py: 'losetup', '--find', '--show', image
    # engine/virt/disk/loop.py: 'losetup', '--detach', device
    CommandFilter("/sbin/losetup", "root"),

    # engine/virt/disk/guestfs.py: 'guestmount', '--rw', '-a', image, '-i'
    # engine/virt/disk/guestfs.py: 'guestmount', '--rw', '-a', image, '-m' dev
    CommandFilter("/usr/bin/guestmount", "root"),

    # engine/virt/disk/guestfs.py: 'fusermount', 'u', mount_dir
    CommandFilter("/bin/fusermount", "root"),
    CommandFilter("/usr/bin/fusermount", "root"),

    # engine/virt/disk/api.py: 'tee', metadata_path
    # engine/virt/disk/api.py: 'tee', '-a', keyfile
    # engine/virt/disk/api.py: 'tee', netfile
    CommandFilter("/usr/bin/tee", "root"),

    # engine/virt/disk/api.py: 'mkdir', '-p', sshdir
    # engine/virt/disk/api.py: 'mkdir', '-p', netdir
    CommandFilter("/bin/mkdir", "root"),

    # engine/virt/disk/api.py: 'chown', 'root', sshdir
    # engine/virt/disk/api.py: 'chown', 'root:root', netdir
    # engine/virt/libvirt/connection.py: 'chown', os.getuid(), console_log
    # engine/virt/libvirt/connection.py: 'chown', os.getuid(), console_log
    # engine/virt/libvirt/connection.py: 'chown', 'root', basepath('disk')
    # engine/virt/xenapi/vm_utils.py: 'chown', os.getuid(), dev_path
    CommandFilter("/bin/chown", "root"),

    # engine/virt/disk/api.py: 'chmod', '700', sshdir
    # engine/virt/disk/api.py: 'chmod', 755, netdir
    CommandFilter("/bin/chmod", "root"),

    # engine/virt/libvirt/vif.py: 'ip', 'tuntap', 'add', dev, 'mode', 'tap'
    # engine/virt/libvirt/vif.py: 'ip', 'link', 'set', dev, 'up'
    # engine/virt/libvirt/vif.py: 'ip', 'link', 'delete', dev
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

    # engine/virt/libvirt/vif.py: 'tunctl', '-b', '-t', dev
    CommandFilter("/usr/sbin/tunctl", "root"),

    # engine/virt/libvirt/vif.py: 'ovs-vsctl', ...
    # engine/virt/libvirt/vif.py: 'ovs-vsctl', 'del-port', ...
    # engine/network/linux_net.py: 'ovs-vsctl', ....
    CommandFilter("/usr/bin/ovs-vsctl", "root"),

    # engine/virt/libvirt/connection.py: 'dd', "if=%s" % virsh_output, ...
    CommandFilter("/bin/dd", "root"),

    # engine/virt/xenapi/volume_utils.py: 'iscsiadm', '-m', ...
    CommandFilter("/sbin/iscsiadm", "root"),

    # engine/virt/xenapi/vm_utils.py: "parted", "--script", ...
    # engine/virt/xenapi/vm_utils.py: 'parted', '--script', dev_path, ..*.
    CommandFilter("/sbin/parted", "root"),

    # engine/virt/xenapi/vm_utils.py: fdisk %(dev_path)s
    CommandFilter("/sbin/fdisk", "root"),

    # engine/virt/xenapi/vm_utils.py: "e2fsck", "-f", "-p", partition_path
    CommandFilter("/sbin/e2fsck", "root"),

    # engine/virt/xenapi/vm_utils.py: "resize2fs", partition_path
    CommandFilter("/sbin/resize2fs", "root"),

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
    ]

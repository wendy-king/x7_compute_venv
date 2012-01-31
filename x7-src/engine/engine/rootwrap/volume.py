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


from engine.rootwrap.filters import CommandFilter

filters = [
    # engine/volume/iscsi.py: iscsi_helper '--op' ...
    CommandFilter("/usr/sbin/ietadm", "root"),
    CommandFilter("/usr/sbin/tgtadm", "root"),

    # engine/volume/driver.py: 'vgs', '--noheadings', '-o', 'name'
    CommandFilter("/sbin/vgs", "root"),

    # engine/volume/driver.py: 'lvcreate', '-L', sizestr, '-n', volume_name,..
    # engine/volume/driver.py: 'lvcreate', '-L', ...
    CommandFilter("/sbin/lvcreate", "root"),

    # engine/volume/driver.py: 'dd', 'if=%s' % srcstr, 'of=%s' % deststr,...
    CommandFilter("/bin/dd", "root"),

    # engine/volume/driver.py: 'lvremove', '-f', "%s/%s" % ...
    CommandFilter("/sbin/lvremove", "root"),

    # engine/volume/driver.py: 'lvdisplay', '--noheading', '-C', '-o', 'Attr',..
    CommandFilter("/sbin/lvdisplay", "root"),

    # engine/volume/driver.py: 'iscsiadm', '-m', 'discovery', '-t',...
    # engine/volume/driver.py: 'iscsiadm', '-m', 'node', '-T', ...
    CommandFilter("/sbin/iscsiadm", "root"),

    # engine/volume/driver.py:'/var/lib/zadara/bin/zadara_sncfg', *
    # sudoers does not allow zadara_sncfg yet
    ]

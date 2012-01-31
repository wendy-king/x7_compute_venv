# vim: tabstop=4 shiftwidth=4 softtabstop=4

# Copyright 2011 X7, LLC
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

import os.path
import unittest

import stubout

from tank.api.middleware import version_negotiation
from tank.api.v1 import images
from tank.api.v1 import members
from tank.common import config
from tank.image_cache import pruner


class TestPasteApp(unittest.TestCase):

    def setUp(self):
        self.stubs = stubout.StubOutForTesting()

    def tearDown(self):
        self.stubs.UnsetAll()

    def test_load_paste_app(self):
        conf = config.TankConfigOpts()
        conf(['--config-file',
              os.path.join(os.getcwd(), 'etc/tank-api.conf')])

        self.stubs.Set(config, 'setup_logging', lambda *a: None)
        self.stubs.Set(images, 'create_resource', lambda *a: None)
        self.stubs.Set(members, 'create_resource', lambda *a: None)

        app = config.load_paste_app(conf, 'tank-api')

        self.assertEquals(version_negotiation.VersionNegotiationFilter,
                          type(app))

    def test_load_paste_app_with_conf_name(self):
        def fake_join(*args):
            if len(args) == 2 and \
                    args[0].endswith('.tank') and \
                    args[1] == 'tank-cache.conf':
                return os.path.join(os.getcwd(), 'etc', args[1])
            else:
                return orig_join(*args)

        orig_join = os.path.join
        self.stubs.Set(os.path, 'join', fake_join)

        conf = config.TankCacheConfigOpts()
        conf([])

        self.stubs.Set(config, 'setup_logging', lambda *a: None)
        self.stubs.Set(pruner, 'Pruner', lambda conf, **lc: 'pruner')

        app = config.load_paste_app(conf, 'tank-pruner')

        self.assertEquals('pruner', app)

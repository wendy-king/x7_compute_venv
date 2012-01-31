# vim: tabstop=4 shiftwidth=4 softtabstop=4

# Copyright 2010 United States Government as represented by the
# Administrator of the National Aeronautics and Space Administration.
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

from engine import flags

FLAGS = flags.FLAGS

flags.DECLARE('volume_driver', 'engine.volume.manager')
FLAGS['volume_driver'].SetDefault('engine.volume.driver.FakeISCSIDriver')
FLAGS['connection_type'].SetDefault('fake')
FLAGS['fake_rabbit'].SetDefault(True)
FLAGS['rpc_backend'].SetDefault('engine.rpc.impl_fake')
flags.DECLARE('auth_driver', 'engine.auth.manager')
FLAGS['auth_driver'].SetDefault('engine.auth.dbdriver.DbDriver')
flags.DECLARE('network_size', 'engine.network.manager')
flags.DECLARE('num_networks', 'engine.network.manager')
flags.DECLARE('fake_network', 'engine.network.manager')
FLAGS['network_size'].SetDefault(8)
FLAGS['num_networks'].SetDefault(2)
FLAGS['fake_network'].SetDefault(True)
FLAGS['image_service'].SetDefault('engine.image.fake.FakeImageService')
flags.DECLARE('iscsi_num_targets', 'engine.volume.driver')
FLAGS['iscsi_num_targets'].SetDefault(8)
FLAGS['verbose'].SetDefault(True)
FLAGS['sqlite_db'].SetDefault("tests.sqlite")
FLAGS['use_ipv6'].SetDefault(True)
FLAGS['flat_network_bridge'].SetDefault('br100')
FLAGS['sqlite_synchronous'].SetDefault(False)
flags.DECLARE('policy_file', 'engine.policy')
FLAGS['policy_file'].SetDefault('engine/tests/policy.json')

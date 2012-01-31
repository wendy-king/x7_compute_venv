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

from lxml import etree
import webob.exc

from engine import context
from engine import exception
from engine import flags
from engine import log as logging
from engine import test
from engine.api.x7.v2.contrib import hosts as os_hosts
from engine.scheduler import api as scheduler_api


FLAGS = flags.FLAGS
LOG = logging.getLogger('engine.tests.hosts')
# Simulate the hosts returned by the zone manager.
HOST_LIST = [
        {"host_name": "host_c1", "service": "compute"},
        {"host_name": "host_c2", "service": "compute"},
        {"host_name": "host_v1", "service": "volume"},
        {"host_name": "host_v2", "service": "volume"}]


def stub_get_host_list(req):
    return HOST_LIST


def stub_set_host_enabled(context, host, enabled):
    # We'll simulate success and failure by assuming
    # that 'host_c1' always succeeds, and 'host_c2'
    # always fails
    fail = (host == "host_c2")
    status = "enabled" if (enabled ^ fail) else "disabled"
    return status


def stub_host_power_action(context, host, action):
    return action


class FakeRequest(object):
    environ = {"engine.context": context.get_admin_context()}


class HostTestCase(test.TestCase):
    """Test Case for hosts."""

    def setUp(self):
        super(HostTestCase, self).setUp()
        self.controller = os_hosts.HostController()
        self.req = FakeRequest()
        self.stubs.Set(scheduler_api, 'get_host_list', stub_get_host_list)
        self.stubs.Set(self.controller.compute_api, 'set_host_enabled',
                stub_set_host_enabled)
        self.stubs.Set(self.controller.compute_api, 'host_power_action',
                stub_host_power_action)

    def test_list_hosts(self):
        """Verify that the compute hosts are returned."""
        hosts = os_hosts._list_hosts(self.req)
        self.assertEqual(hosts, HOST_LIST)

        compute_hosts = os_hosts._list_hosts(self.req, "compute")
        expected = [host for host in HOST_LIST
                if host["service"] == "compute"]
        self.assertEqual(compute_hosts, expected)

    def test_disable_host(self):
        dis_body = {"status": "disable"}
        result_c1 = self.controller.update(self.req, "host_c1", body=dis_body)
        self.assertEqual(result_c1["status"], "disabled")
        result_c2 = self.controller.update(self.req, "host_c2", body=dis_body)
        self.assertEqual(result_c2["status"], "enabled")

    def test_enable_host(self):
        en_body = {"status": "enable"}
        result_c1 = self.controller.update(self.req, "host_c1", body=en_body)
        self.assertEqual(result_c1["status"], "enabled")
        result_c2 = self.controller.update(self.req, "host_c2", body=en_body)
        self.assertEqual(result_c2["status"], "disabled")

    def test_host_startup(self):
        self.flags(allow_admin_api=True)
        result = self.controller.startup(self.req, "host_c1")
        self.assertEqual(result["power_action"], "startup")

    def test_host_shutdown(self):
        self.flags(allow_admin_api=True)
        result = self.controller.shutdown(self.req, "host_c1")
        self.assertEqual(result["power_action"], "shutdown")

    def test_host_reboot(self):
        self.flags(allow_admin_api=True)
        result = self.controller.reboot(self.req, "host_c1")
        self.assertEqual(result["power_action"], "reboot")

    def test_bad_status_value(self):
        bad_body = {"status": "bad"}
        self.assertRaises(webob.exc.HTTPBadRequest, self.controller.update,
                self.req, "host_c1", body=bad_body)

    def test_bad_update_key(self):
        bad_body = {"crazy": "bad"}
        self.assertRaises(webob.exc.HTTPBadRequest, self.controller.update,
                self.req, "host_c1", body=bad_body)

    def test_bad_host(self):
        self.assertRaises(exception.HostNotFound, self.controller.update,
                self.req, "bogus_host_name", body={"status": "disable"})


class HostSerializerTest(test.TestCase):
    def setUp(self):
        super(HostSerializerTest, self).setUp()
        self.deserializer = os_hosts.HostDeserializer()

    def test_index_serializer(self):
        serializer = os_hosts.HostIndexTemplate()
        text = serializer.serialize(HOST_LIST)

        tree = etree.fromstring(text)

        self.assertEqual('hosts', tree.tag)
        self.assertEqual(len(HOST_LIST), len(tree))
        for i in range(len(HOST_LIST)):
            self.assertEqual('host', tree[i].tag)
            self.assertEqual(HOST_LIST[i]['host_name'],
                             tree[i].get('host_name'))
            self.assertEqual(HOST_LIST[i]['service'],
                             tree[i].get('service'))

    def test_update_serializer(self):
        exemplar = dict(host='host_c1', status='enabled')
        serializer = os_hosts.HostUpdateTemplate()
        text = serializer.serialize(exemplar)

        tree = etree.fromstring(text)

        self.assertEqual('host', tree.tag)
        for key, value in exemplar.items():
            self.assertEqual(value, tree.get(key))

    def test_action_serializer(self):
        exemplar = dict(host='host_c1', power_action='reboot')
        serializer = os_hosts.HostActionTemplate()
        text = serializer.serialize(exemplar)

        tree = etree.fromstring(text)

        self.assertEqual('host', tree.tag)
        for key, value in exemplar.items():
            self.assertEqual(value, tree.get(key))

    def test_update_deserializer(self):
        exemplar = dict(status='enabled', foo='bar')
        intext = ("<?xml version='1.0' encoding='UTF-8'?>\n"
                  '<updates><status>enabled</status><foo>bar</foo></updates>')
        result = self.deserializer.deserialize(intext)

        self.assertEqual(dict(body=exemplar), result)

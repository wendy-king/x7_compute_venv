# vim: tabstop=4 shiftwidth=4 softtabstop=4

# Copyright 2011, X7 LLC.
#
#    Licensed under the Apache License, Version 2.0 (the "License"); you may
#    not use this file except in compliance with the License. You may obtain
#    a copy of the License at
#         http://www.apache.org/licenses/LICENSE-2.0
#
#    Unless required by applicable law or agreed to in writing, software
#    distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
#    WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
#    License for the specific language governing permissions and limitations
#    under the License.


import json

import kombu.connection
import kombu.entity

from tank.common import cfg
from tank.notifier import strategy


class RabbitStrategy(strategy.Strategy):
    """A notifier that puts a message on a queue when called."""

    opts = [
        cfg.StrOpt('rabbit_host', default='localhost'),
        cfg.IntOpt('rabbit_port', default=5672),
        cfg.BoolOpt('rabbit_use_ssl', default=False),
        cfg.StrOpt('rabbit_userid', default='guest'),
        cfg.StrOpt('rabbit_password', default='guest'),
        cfg.StrOpt('rabbit_virtual_host', default='/'),
        cfg.StrOpt('rabbit_notification_exchange', default='tank'),
        cfg.StrOpt('rabbit_notification_topic', default='tank_notifications')
        ]

    def __init__(self, conf):
        """Initialize the rabbit notification strategy."""
        self._conf = conf
        self._conf.register_opts(self.opts)

        self.topic = self._conf.rabbit_notification_topic
        self.connect()

    def connect(self):
        self.connection = kombu.connection.BrokerConnection(
            hostname=self._conf.rabbit_host,
            userid=self._conf.rabbit_userid,
            password=self._conf.rabbit_password,
            virtual_host=self._conf.rabbit_virtual_host,
            ssl=self._conf.rabbit_use_ssl)
        self.channel = self.connection.channel()

        self.exchange = kombu.entity.Exchange(
            channel=self.channel,
            type="topic",
            name=self._conf.rabbit_notification_exchange)
        self.exchange.declare()

    def _send_message(self, message, priority):
        routing_key = "%s.%s" % (self.topic, priority.lower())

        # NOTE(jerdfelt): Normally the consumer would create the queue, but
        # we do this to ensure that messages don't get dropped if the
        # consumer is started after we do
        queue = kombu.entity.Queue(
            channel=self.channel,
            exchange=self.exchange,
            durable=True,
            name=routing_key,
            routing_key=routing_key)
        queue.declare()

        msg = self.exchange.Message(json.dumps(message))
        self.exchange.publish(msg, routing_key=routing_key)

    def warn(self, msg):
        self._send_message(msg, "WARN")

    def info(self, msg):
        self._send_message(msg, "INFO")

    def error(self, msg):
        self._send_message(msg, "ERROR")

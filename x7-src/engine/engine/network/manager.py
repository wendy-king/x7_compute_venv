# vim: tabstop=4 shiftwidth=4 softtabstop=4

# Copyright (c) 2011 X.commerce, a business unit of eBay Inc.
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

"""Network Hosts are responsible for allocating ips and setting up network.

There are multiple backend drivers that handle specific types of networking
topologies.  All of the network commands are issued to a subclass of
:class:`NetworkManager`.

**Related Flags**

:network_driver:  Driver to use for network creation
:flat_network_bridge:  Bridge device for simple network instances
:flat_interface:  FlatDhcp will bridge into this interface if set
:flat_network_dns:  Dns for simple network
:vlan_start:  First VLAN for private networks
:vpn_ip:  Public IP for the cloudpipe VPN servers
:vpn_start:  First Vpn port for private networks
:cnt_vpn_clients:  Number of addresses reserved for vpn clients
:network_size:  Number of addresses in each private subnet
:floating_range:  Floating IP address block
:fixed_range:  Fixed IP address block
:date_dhcp_on_disassociate:  Whether to update dhcp when fixed_ip
                             is disassociated
:fixed_ip_disassociate_timeout:  Seconds after which a deallocated ip
                                 is disassociated
:create_unique_mac_address_attempts:  Number of times to attempt creating
                                      a unique mac address

"""

import datetime
import itertools
import math
import netaddr
import random
import re
import socket
from eventlet import greenpool

from engine.compute import api as compute_api
from engine.compute import instance_types
from engine import context
from engine import db
from engine import exception
from engine import flags
from engine import ipv6
from engine import log as logging
from engine import manager
from engine.network import api as network_api
from engine.network import model as network_model
from engine import quota
from engine import utils
from engine import rpc


LOG = logging.getLogger("engine.network.manager")


FLAGS = flags.FLAGS
flags.DEFINE_string('flat_network_bridge', None,
                    'Bridge for simple network instances')
flags.DEFINE_string('flat_network_dns', '8.8.4.4',
                    'Dns for simple network')
flags.DEFINE_bool('flat_injected', False,
                  'Whether to attempt to inject network setup into guest')
flags.DEFINE_string('flat_interface', None,
                    'FlatDhcp will bridge into this interface if set')
flags.DEFINE_integer('vlan_start', 100, 'First VLAN for private networks')
flags.DEFINE_string('vlan_interface', None,
                    'vlans will bridge into this interface if set')
flags.DEFINE_integer('num_networks', 1, 'Number of networks to support')
flags.DEFINE_string('vpn_ip', '$my_ip',
                    'Public IP for the cloudpipe VPN servers')
flags.DEFINE_integer('vpn_start', 1000, 'First Vpn port for private networks')
flags.DEFINE_bool('multi_host', False,
                  'Default value for multi_host in networks')
flags.DEFINE_integer('network_size', 256,
                        'Number of addresses in each private subnet')
flags.DEFINE_string('floating_range', '4.4.4.0/24',
                    'Floating IP address block')
flags.DEFINE_string('default_floating_pool', 'engine',
                    'Default pool for floating ips')
flags.DEFINE_string('fixed_range', '10.0.0.0/8', 'Fixed IP address block')
flags.DEFINE_string('fixed_range_v6', 'fd00::/48', 'Fixed IPv6 address block')
flags.DEFINE_string('gateway', None, 'Default IPv4 gateway')
flags.DEFINE_string('gateway_v6', None, 'Default IPv6 gateway')
flags.DEFINE_integer('cnt_vpn_clients', 0,
                     'Number of addresses reserved for vpn clients')
flags.DEFINE_bool('update_dhcp_on_disassociate', False,
                  'Whether to update dhcp when fixed_ip is disassociated')
flags.DEFINE_integer('fixed_ip_disassociate_timeout', 600,
                     'Seconds after which a deallocated ip is disassociated')
flags.DEFINE_integer('create_unique_mac_address_attempts', 5,
                     'Number of attempts to create unique mac address')
flags.DEFINE_bool('auto_assign_floating_ip', False,
                  'Autoassigning floating ip to VM')
flags.DEFINE_string('network_host', socket.gethostname(),
                    'Network host to use for ip allocation in flat modes')
flags.DEFINE_bool('fake_call', False,
                  'If True, skip using the queue and make local calls')
flags.DEFINE_bool('force_dhcp_release', False,
                  'If True, send a dhcp release on instance termination')
flags.DEFINE_string('dhcp_domain',
                    'enginelocal',
                    'domain to use for building the hostnames')


class AddressAlreadyAllocated(exception.Error):
    """Address was already allocated."""
    pass


class RPCAllocateFixedIP(object):
    """Mixin class originally for FlatDCHP and VLAN network managers.

    used since they share code to RPC.call allocate_fixed_ip on the
    correct network host to configure dnsmasq
    """
    def _allocate_fixed_ips(self, context, instance_id, host, networks,
                            **kwargs):
        """Calls allocate_fixed_ip once for each network."""
        green_pool = greenpool.GreenPool()

        vpn = kwargs.get('vpn')
        requested_networks = kwargs.get('requested_networks')

        for network in networks:
            address = None
            if requested_networks is not None:
                for address in (fixed_ip for (uuid, fixed_ip) in \
                              requested_networks if network['uuid'] == uuid):
                    break

            # NOTE(vish): if we are not multi_host pass to the network host
            if not network['multi_host']:
                host = network['host']
            # NOTE(vish): if there is no network host, set one
            if host is None:
                host = rpc.call(context, FLAGS.network_topic,
                                {'method': 'set_network_host',
                                 'args': {'network_ref': network}})
            if host != self.host:
                # need to call allocate_fixed_ip to correct network host
                topic = self.db.queue_get_for(context,
                                              FLAGS.network_topic,
                                              host)
                args = {}
                args['instance_id'] = instance_id
                args['network_id'] = network['id']
                args['address'] = address
                args['vpn'] = vpn

                green_pool.spawn_n(rpc.call, context, topic,
                                   {'method': '_rpc_allocate_fixed_ip',
                                    'args': args})
            else:
                # i am the correct host, run here
                self.allocate_fixed_ip(context, instance_id, network,
                                       vpn=vpn, address=address)

        # wait for all of the allocates (if any) to finish
        green_pool.waitall()

    def _rpc_allocate_fixed_ip(self, context, instance_id, network_id,
                               **kwargs):
        """Sits in between _allocate_fixed_ips and allocate_fixed_ip to
        perform network lookup on the far side of rpc.
        """
        network = self.db.network_get(context, network_id)
        return self.allocate_fixed_ip(context, instance_id, network, **kwargs)


class FloatingIP(object):
    """Mixin class for adding floating IP functionality to a manager."""
    def init_host_floating_ips(self):
        """Configures floating ips owned by host."""

        admin_context = context.get_admin_context()
        try:
            floating_ips = self.db.floating_ip_get_all_by_host(admin_context,
                                                               self.host)
        except exception.NotFound:
            return

        for floating_ip in floating_ips:
            if floating_ip.get('fixed_ip', None):
                fixed_address = floating_ip['fixed_ip']['address']
                # NOTE(vish): The False here is because we ignore the case
                #             that the ip is already bound.
                self.driver.bind_floating_ip(floating_ip['address'],
                                             floating_ip['interface'],
                                             False)
                self.driver.ensure_floating_forward(floating_ip['address'],
                                                    fixed_address)

    def allocate_for_instance(self, context, **kwargs):
        """Handles allocating the floating IP resources for an instance.

        calls super class allocate_for_instance() as well

        rpc.called by network_api
        """
        instance_id = kwargs.get('instance_id')
        project_id = kwargs.get('project_id')
        requested_networks = kwargs.get('requested_networks')
        LOG.debug(_("floating IP allocation for instance |%s|"), instance_id,
                                                               context=context)
        # call the next inherited class's allocate_for_instance()
        # which is currently the NetworkManager version
        # do this first so fixed ip is already allocated
        nw_info = \
               super(FloatingIP, self).allocate_for_instance(context, **kwargs)
        if FLAGS.auto_assign_floating_ip:
            # allocate a floating ip
            floating_address = self.allocate_floating_ip(context, project_id)
            # set auto_assigned column to true for the floating ip
            self.db.floating_ip_set_auto_assigned(context, floating_address)

            # get the first fixed address belonging to the instance
            for nw, info in nw_info:
                if info.get('ips'):
                    fixed_address = info['ips'][0]['ip']
                    break

            # associate the floating ip to fixed_ip
            self.associate_floating_ip(context,
                                       floating_address,
                                       fixed_address,
                                       affect_auto_assigned=True)
        return nw_info

    def deallocate_for_instance(self, context, **kwargs):
        """Handles deallocating floating IP resources for an instance.

        calls super class deallocate_for_instance() as well.

        rpc.called by network_api
        """
        instance_id = kwargs.get('instance_id')
        LOG.debug(_("floating IP deallocation for instance |%s|"), instance_id,
                                                               context=context)

        try:
            fixed_ips = self.db.fixed_ip_get_by_instance(context, instance_id)
        except exception.FixedIpNotFoundForInstance:
            fixed_ips = []
        # add to kwargs so we can pass to super to save a db lookup there
        kwargs['fixed_ips'] = fixed_ips
        for fixed_ip in fixed_ips:
            # disassociate floating ips related to fixed_ip
            for floating_ip in fixed_ip.floating_ips:
                address = floating_ip['address']
                self.disassociate_floating_ip(context, address, True)
                # deallocate if auto_assigned
                if floating_ip['auto_assigned']:
                    self.release_floating_ip(context, address, True)

        # call the next inherited class's deallocate_for_instance()
        # which is currently the NetworkManager version
        # call this after so floating IPs are handled first
        super(FloatingIP, self).deallocate_for_instance(context, **kwargs)

    def _floating_ip_owned_by_project(self, context, floating_ip):
        """Raises if floating ip does not belong to project"""
        if floating_ip['project_id'] != context.project_id:
            if floating_ip['project_id'] is None:
                LOG.warn(_('Address |%(address)s| is not allocated'),
                           {'address': floating_ip['address']})
                raise exception.NotAuthorized()
            else:
                LOG.warn(_('Address |%(address)s| is not allocated to your '
                           'project |%(project)s|'),
                           {'address': floating_ip['address'],
                           'project': context.project_id})
                raise exception.NotAuthorized()

    def allocate_floating_ip(self, context, project_id, pool=None):
        """Gets a floating ip from the pool."""
        # NOTE(tr3buchet): all network hosts in zone now use the same pool
        LOG.debug("QUOTA: %s" % quota.allowed_floating_ips(context, 1))
        if quota.allowed_floating_ips(context, 1) < 1:
            LOG.warn(_('Quota exceeded for %s, tried to allocate '
                       'address'),
                     context.project_id)
            raise exception.QuotaError(_('Address quota exceeded. You cannot '
                                     'allocate any more addresses'))
        pool = pool or FLAGS.default_floating_pool
        return self.db.floating_ip_allocate_address(context,
                                                    project_id,
                                                    pool)

    def deallocate_floating_ip(self, context, address,
                               affect_auto_assigned=False):
        """Returns an floating ip to the pool."""
        floating_ip = self.db.floating_ip_get_by_address(context, address)

        # handle auto_assigned
        if not affect_auto_assigned and floating_ip.get('auto_assigned'):
            return

        # make sure project ownz this floating ip (allocated)
        self._floating_ip_owned_by_project(context, floating_ip)

        # make sure floating ip is not associated
        if floating_ip['fixed_ip_id']:
            floating_address = floating_ip['address']
            raise exception.FloatingIpAssociated(address=floating_address)

        self.db.floating_ip_deallocate(context, address)

    def associate_floating_ip(self, context, floating_address, fixed_address,
                                                 affect_auto_assigned=False):
        """Associates a floating ip with a fixed ip.

        Makes sure everything makes sense then calls _associate_floating_ip,
        rpc'ing to correct host if i'm not it.
        """
        floating_ip = self.db.floating_ip_get_by_address(context,
                                                         floating_address)
        # handle auto_assigned
        if not affect_auto_assigned and floating_ip.get('auto_assigned'):
            return

        # make sure project ownz this floating ip (allocated)
        self._floating_ip_owned_by_project(context, floating_ip)

        # make sure floating ip isn't already associated
        if floating_ip['fixed_ip_id']:
            raise exception.FloatingIpAssociated(address=floating_address)

        fixed_ip = self.db.fixed_ip_get_by_address(context, fixed_address)

        # send to correct host, unless i'm the correct host
        if fixed_ip['network']['multi_host']:
            instance = self.db.instance_get(context, fixed_ip['instance_id'])
            host = instance['host']
        else:
            host = fixed_ip['network']['host']
        interface = floating_ip['interface']
        if host == self.host:
            # i'm the correct host
            self._associate_floating_ip(context, floating_address,
                                        fixed_address, interface)
        else:
            # send to correct host
            rpc.cast(context,
                     self.db.queue_get_for(context, FLAGS.network_topic, host),
                     {'method': '_associate_floating_ip',
                      'args': {'floating_address': floating_address,
                               'fixed_address': fixed_address,
                               'interface': interface}})

    def _associate_floating_ip(self, context, floating_address, fixed_address,
                               interface):
        """Performs db and driver calls to associate floating ip & fixed ip"""
        # associate floating ip
        self.db.floating_ip_fixed_ip_associate(context,
                                               floating_address,
                                               fixed_address,
                                               self.host)
        # gogo driver time
        self.driver.bind_floating_ip(floating_address, interface)
        self.driver.ensure_floating_forward(floating_address, fixed_address)

    def disassociate_floating_ip(self, context, address,
                                 affect_auto_assigned=False):
        """Disassociates a floating ip from its fixed ip.

        Makes sure everything makes sense then calls _disassociate_floating_ip,
        rpc'ing to correct host if i'm not it.
        """
        floating_ip = self.db.floating_ip_get_by_address(context, address)

        # handle auto assigned
        if not affect_auto_assigned and floating_ip.get('auto_assigned'):
            return

        # make sure project ownz this floating ip (allocated)
        self._floating_ip_owned_by_project(context, floating_ip)

        # make sure floating ip is associated
        if not floating_ip.get('fixed_ip_id'):
            floating_address = floating_ip['address']
            raise exception.FloatingIpNotAssociated(address=floating_address)

        fixed_ip = self.db.fixed_ip_get(context, floating_ip['fixed_ip_id'])

        # send to correct host, unless i'm the correct host
        if fixed_ip['network']['multi_host']:
            instance = self.db.instance_get(context, fixed_ip['instance_id'])
            host = instance['host']
        else:
            host = fixed_ip['network']['host']
        interface = floating_ip['interface']
        if host == self.host:
            # i'm the correct host
            self._disassociate_floating_ip(context, address, interface)
        else:
            # send to correct host
            rpc.cast(context,
                     self.db.queue_get_for(context, FLAGS.network_topic, host),
                     {'method': '_disassociate_floating_ip',
                      'args': {'address': address,
                               'interface': interface}})

    def _disassociate_floating_ip(self, context, address, interface):
        """Performs db and driver calls to disassociate floating ip"""
        # disassociate floating ip
        fixed_address = self.db.floating_ip_disassociate(context, address)

        # go go driver time
        self.driver.unbind_floating_ip(address, interface)
        self.driver.remove_floating_forward(address, fixed_address)

    def get_floating_ip(self, context, id):
        """Returns a floating IP as a dict"""
        return dict(self.db.floating_ip_get(context, id).iteritems())

    def get_floating_pools(self, context):
        """Returns list of floating pools"""
        pools = self.db.floating_ip_get_pools(context)
        return [dict(pool.iteritems()) for pool in pools]

    def get_floating_ip_by_address(self, context, address):
        """Returns a floating IP as a dict"""
        return dict(self.db.floating_ip_get_by_address(context,
                                                       address).iteritems())

    def get_floating_ips_by_project(self, context):
        """Returns the floating IPs allocated to a project"""
        ips = self.db.floating_ip_get_all_by_project(context,
                                                     context.project_id)
        return [dict(ip.iteritems()) for ip in ips]

    def get_floating_ips_by_fixed_address(self, context, fixed_address):
        """Returns the floating IPs associated with a fixed_address"""
        floating_ips = self.db.floating_ip_get_by_fixed_address(context,
                                                                fixed_address)
        return [floating_ip['address'] for floating_ip in floating_ips]

    def get_dns_zones(self, context):
        return self.floating_dns_manager.get_zones()

    def add_dns_entry(self, context, address, dns_name, dns_type, dns_zone):
        self.floating_dns_manager.create_entry(dns_name, address,
                                               dns_type, dns_zone)

    def modify_dns_entry(self, context, address, dns_name, dns_zone):
        self.floating_dns_manager.modify_address(dns_name, address,
                                                 dns_zone)

    def delete_dns_entry(self, context, dns_name, dns_zone):
        self.floating_dns_manager.delete_entry(dns_name, dns_zone)

    def get_dns_entries_by_address(self, context, address, dns_zone):
        return self.floating_dns_manager.get_entries_by_address(address,
                                                                dns_zone)

    def get_dns_entries_by_name(self, context, name, dns_zone):
        return self.floating_dns_manager.get_entries_by_name(name,
                                                             dns_zone)


class NetworkManager(manager.SchedulerDependentManager):
    """Implements common network manager functionality.

    This class must be subclassed to support specific topologies.

    host management:
        hosts configure themselves for networks they are assigned to in the
        table upon startup. If there are networks in the table which do not
        have hosts, those will be filled in and have hosts configured
        as the hosts pick them up one at time during their periodic task.
        The one at a time part is to flatten the layout to help scale
    """

    # If True, this manager requires VIF to create a bridge.
    SHOULD_CREATE_BRIDGE = False

    # If True, this manager requires VIF to create VLAN tag.
    SHOULD_CREATE_VLAN = False

    timeout_fixed_ips = True

    def __init__(self, network_driver=None, *args, **kwargs):
        if not network_driver:
            network_driver = FLAGS.network_driver
        self.driver = utils.import_object(network_driver)
        temp = utils.import_object(FLAGS.instance_dns_manager)
        self.instance_dns_manager = temp
        temp = utils.import_object(FLAGS.floating_ip_dns_manager)
        self.floating_dns_manager = temp
        self.network_api = network_api.API()
        self.compute_api = compute_api.API()
        super(NetworkManager, self).__init__(service_name='network',
                                                *args, **kwargs)

    @utils.synchronized('get_dhcp')
    def _get_dhcp_ip(self, context, network_ref, host=None):
        """Get the proper dhcp address to listen on."""
        # NOTE(vish): this is for compatibility
        if not network_ref['multi_host']:
            return network_ref['gateway']

        if not host:
            host = self.host
        network_id = network_ref['id']
        try:
            fip = self.db.fixed_ip_get_by_network_host(context,
                                                       network_id,
                                                       host)
            return fip['address']
        except exception.FixedIpNotFoundForNetworkHost:
            elevated = context.elevated()
            return self.db.fixed_ip_associate_pool(elevated,
                                                   network_id,
                                                   host=host)

    def get_dhcp_leases(self, ctxt, network_ref):
        """Broker the request to the driver to fetch the dhcp leases"""
        return self.driver.get_dhcp_leases(ctxt, network_ref)

    def init_host(self):
        """Do any initialization that needs to be run if this is a
        standalone service.
        """
        # NOTE(vish): Set up networks for which this host already has
        #             an ip address.
        ctxt = context.get_admin_context()
        for network in self.db.network_get_all_by_host(ctxt, self.host):
            self._setup_network(ctxt, network)

    @manager.periodic_task
    def _disassociate_stale_fixed_ips(self, context):
        if self.timeout_fixed_ips:
            now = utils.utcnow()
            timeout = FLAGS.fixed_ip_disassociate_timeout
            time = now - datetime.timedelta(seconds=timeout)
            num = self.db.fixed_ip_disassociate_all_by_timeout(context,
                                                               self.host,
                                                               time)
            if num:
                LOG.debug(_('Disassociated %s stale fixed ip(s)'), num)

    def set_network_host(self, context, network_ref):
        """Safely sets the host of the network."""
        LOG.debug(_('setting network host'), context=context)
        host = self.db.network_set_host(context,
                                        network_ref['id'],
                                        self.host)
        return host

    def _do_trigger_security_group_members_refresh_for_instance(self,
                                                                instance_id):
        admin_context = context.get_admin_context()
        instance_ref = self.db.instance_get(admin_context, instance_id)
        groups = instance_ref['security_groups']
        group_ids = [group['id'] for group in groups]
        self.compute_api.trigger_security_group_members_refresh(admin_context,
                                                                    group_ids)

    def get_floating_ips_by_fixed_address(self, context, fixed_address):
        # NOTE(jkoelker) This is just a stub function. Managers supporting
        #                floating ips MUST override this or use the Mixin
        return []

    def get_instance_uuids_by_ip_filter(self, context, filters):
        fixed_ip_filter = filters.get('fixed_ip')
        ip_filter = re.compile(str(filters.get('ip')))
        ipv6_filter = re.compile(str(filters.get('ip6')))

        # NOTE(jkoelker) Should probably figure out a better way to do
        #                this. But for now it "works", this could suck on
        #                large installs.

        vifs = self.db.virtual_interface_get_all(context)
        results = []

        for vif in vifs:
            if vif['instance_id'] is None:
                continue

            network = self.db.network_get(context, vif['network_id'])
            fixed_ipv6 = None
            if network['cidr_v6'] is not None:
                fixed_ipv6 = ipv6.to_global(network['cidr_v6'],
                                            vif['address'],
                                            context.project_id)

            if fixed_ipv6 and ipv6_filter.match(fixed_ipv6):
                # NOTE(jkoelker) Will need to update for the UUID flip
                results.append({'instance_id': vif['instance_id'],
                                'ip': fixed_ipv6})

            for fixed_ip in vif['fixed_ips']:
                if not fixed_ip or not fixed_ip['address']:
                    continue
                if fixed_ip['address'] == fixed_ip_filter:
                    results.append({'instance_id': vif['instance_id'],
                                    'ip': fixed_ip['address']})
                    continue
                if ip_filter.match(fixed_ip['address']):
                    results.append({'instance_id': vif['instance_id'],
                                    'ip': fixed_ip['address']})
                    continue
                for floating_ip in fixed_ip.get('floating_ips', []):
                    if not floating_ip or not floating_ip['address']:
                        continue
                    if ip_filter.match(floating_ip['address']):
                        results.append({'instance_id': vif['instance_id'],
                                        'ip': floating_ip['address']})
                        continue

        # NOTE(jkoelker) Until we switch over to instance_uuid ;)
        ids = [res['instance_id'] for res in results]
        uuid_map = self.db.instance_get_id_to_uuid_mapping(context, ids)
        for res in results:
            res['instance_uuid'] = uuid_map.get(res['instance_id'])
        return results

    def _get_networks_for_instance(self, context, instance_id, project_id,
                                   requested_networks=None):
        """Determine & return which networks an instance should connect to."""
        # TODO(tr3buchet) maybe this needs to be updated in the future if
        #                 there is a better way to determine which networks
        #                 a non-vlan instance should connect to
        if requested_networks is not None and len(requested_networks) != 0:
            network_uuids = [uuid for (uuid, fixed_ip) in requested_networks]
            networks = self.db.network_get_all_by_uuids(context, network_uuids)
        else:
            try:
                networks = self.db.network_get_all(context)
            except exception.NoNetworksFound:
                return []
        # return only networks which are not vlan networks
        return [network for network in networks if
                not network['vlan']]

    def allocate_for_instance(self, context, **kwargs):
        """Handles allocating the various network resources for an instance.

        rpc.called by network_api
        """
        instance_id = kwargs.pop('instance_id')
        instance_uuid = kwargs.pop('instance_uuid')
        host = kwargs.pop('host')
        project_id = kwargs.pop('project_id')
        type_id = kwargs.pop('instance_type_id')
        requested_networks = kwargs.get('requested_networks')
        vpn = kwargs.pop('vpn')
        admin_context = context.elevated()
        LOG.debug(_("network allocations for instance %s"), instance_id,
                                                            context=context)
        networks = self._get_networks_for_instance(admin_context,
                                        instance_id, project_id,
                                        requested_networks=requested_networks)
        self._allocate_mac_addresses(context, instance_id, networks)
        self._allocate_fixed_ips(admin_context, instance_id,
                                 host, networks, vpn=vpn,
                                 requested_networks=requested_networks)
        return self.get_instance_nw_info(context, instance_id, instance_uuid,
                                         type_id, host)

    def deallocate_for_instance(self, context, **kwargs):
        """Handles deallocating various network resources for an instance.

        rpc.called by network_api
        kwargs can contain fixed_ips to circumvent another db lookup
        """
        instance_id = kwargs.pop('instance_id')
        try:
            fixed_ips = kwargs.get('fixed_ips') or \
                  self.db.fixed_ip_get_by_instance(context, instance_id)
        except exception.FixedIpNotFoundForInstance:
            fixed_ips = []
        LOG.debug(_("network deallocation for instance |%s|"), instance_id,
                                                               context=context)
        # deallocate fixed ips
        for fixed_ip in fixed_ips:
            self.deallocate_fixed_ip(context, fixed_ip['address'], **kwargs)

        # deallocate vifs (mac addresses)
        self.db.virtual_interface_delete_by_instance(context, instance_id)

    def get_instance_nw_info(self, context, instance_id, instance_uuid,
                             instance_type_id, host):
        """Creates network info list for instance.

        called by allocate_for_instance and network_api
        context needs to be elevated
        :returns: network info list [(network,info),(network,info)...]
        where network = dict containing pertinent data from a network db object
        and info = dict containing pertinent networking data
        """
        # TODO(tr3buchet) should handle floating IPs as well?
        try:
            fixed_ips = self.db.fixed_ip_get_by_instance(context, instance_id)
        except exception.FixedIpNotFoundForInstance:
            LOG.warn(_('No fixed IPs for instance %s'), instance_id)
            fixed_ips = []

        vifs = self.db.virtual_interface_get_by_instance(context, instance_id)
        instance_type = instance_types.get_instance_type(instance_type_id)
        network_info = []
        # a vif has an address, instance_id, and network_id
        # it is also joined to the instance and network given by those IDs
        for vif in vifs:
            network = self.db.network_get(context, vif['network_id'])

            if network is None:
                continue

            # determine which of the instance's IPs belong to this network
            network_IPs = [fixed_ip['address'] for fixed_ip in fixed_ips if
                           fixed_ip['network_id'] == network['id']]

            # TODO(tr3buchet) eventually "enabled" should be determined
            def ip_dict(ip):
                return {
                    'ip': ip,
                    'netmask': network['netmask'],
                    'enabled': '1'}

            def ip6_dict():
                return {
                    'ip': ipv6.to_global(network['cidr_v6'],
                                         vif['address'],
                                         network['project_id']),
                    'netmask': network['netmask_v6'],
                    'enabled': '1'}

            def rxtx_cap(instance_type, network):
                try:
                    rxtx_factor = instance_type['rxtx_factor']
                    rxtx_base = network['rxtx_base']
                    return rxtx_factor * rxtx_base
                except (KeyError, TypeError):
                    return 0

            network_dict = {
                'bridge': network['bridge'],
                'id': network['id'],
                'cidr': network['cidr'],
                'cidr_v6': network['cidr_v6'],
                'injected': network['injected'],
                'vlan': network['vlan'],
                'bridge_interface': network['bridge_interface'],
                'multi_host': network['multi_host']}
            if network['multi_host']:
                dhcp_server = self._get_dhcp_ip(context, network, host)
            else:
                dhcp_server = self._get_dhcp_ip(context,
                                                network,
                                                network['host'])
            info = {
                'label': network['label'],
                'gateway': network['gateway'],
                'dhcp_server': dhcp_server,
                'broadcast': network['broadcast'],
                'mac': vif['address'],
                'vif_uuid': vif['uuid'],
                'rxtx_cap': rxtx_cap(instance_type, network),
                'dns': [],
                'ips': [ip_dict(ip) for ip in network_IPs],
                'should_create_bridge': self.SHOULD_CREATE_BRIDGE,
                'should_create_vlan': self.SHOULD_CREATE_VLAN}

            if network['cidr_v6']:
                info['ip6s'] = [ip6_dict()]
            # TODO(tr3buchet): handle ip6 routes here as well
            if network['gateway_v6']:
                info['gateway_v6'] = network['gateway_v6']
            if network['dns1']:
                info['dns'].append(network['dns1'])
            if network['dns2']:
                info['dns'].append(network['dns2'])

            network_info.append((network_dict, info))

        # update instance network cache and return network_info
        nw_info = self.build_network_info_model(context, vifs, fixed_ips,
                                                               instance_type)
        self.db.instance_info_cache_update(context, instance_uuid,
                                          {'network_info': nw_info.as_cache()})

        # TODO(tr3buchet): return model
        return network_info

    def build_network_info_model(self, context, vifs, fixed_ips,
                                                 instance_type):
        """Returns a NetworkInfo object containing all network information
        for an instance"""
        nw_info = network_model.NetworkInfo()
        for vif in vifs:
            network = self.db.network_get(context, vif['network_id'])
            subnets = self._get_subnets_from_network(network)

            # if rxtx_cap data are not set everywhere, set to none
            try:
                rxtx_cap = network['rxtx_base'] * instance_type['rxtx_factor']
            except (TypeError, KeyError):
                rxtx_cap = None

            # determine which of the instance's fixed IPs are on this network
            network_IPs = [fixed_ip['address'] for fixed_ip in fixed_ips if
                           fixed_ip['network_id'] == network['id']]

            # create model FixedIPs from these fixed_ips
            network_IPs = [network_model.FixedIP(address=ip_address)
                           for ip_address in network_IPs]

            # get floating_ips for each fixed_ip
            # add them to the fixed ip
            for fixed_ip in network_IPs:
                fipgbfa = self.db.floating_ip_get_by_fixed_address
                floating_ips = fipgbfa(context, fixed_ip['address'])
                floating_ips = [network_model.IP(address=ip['address'],
                                                 type='floating')
                                for ip in floating_ips]
                for ip in floating_ips:
                    fixed_ip.add_floating_ip(ip)

            # at this point engine networks can only have 2 subnets,
            # one for v4 and one for v6, all ips will belong to the v4 subnet
            # and the v6 subnet contains a single calculated v6 address
            for subnet in subnets:
                if subnet['version'] == 4:
                    # since subnet currently has no IPs, easily add them all
                    subnet['ips'] = network_IPs
                else:
                    v6_addr = ipv6.to_global(subnet['cidr'], vif['address'],
                                                         context.project_id)
                    subnet.add_ip(network_model.FixedIP(address=v6_addr))

            # convert network into a Network model object
            network = network_model.Network(**self._get_network_dict(network))

            # since network currently has no subnets, easily add them all
            network['subnets'] = subnets

            # create the vif model and add to network_info
            vif_dict = {'id': vif['uuid'],
                        'address': vif['address'],
                        'network': network}
            if rxtx_cap:
                vif_dict['rxtx_cap'] = rxtx_cap

            vif = network_model.VIF(**vif_dict)
            nw_info.append(vif)

        return nw_info

    def _get_network_dict(self, network):
        """Returns the dict representing necessary fields from network"""
        network_dict = {'id': network['uuid'],
                        'bridge': network['bridge'],
                        'label': network['label']}

        if network['injected']:
            network_dict['injected'] = network['injected']
        if network['vlan']:
            network_dict['vlan'] = network['vlan']
        if network['bridge_interface']:
            network_dict['bridge_interface'] = network['bridge_interface']
        if network['multi_host']:
            network_dict['multi_host'] = network['multi_host']

        return network_dict

    def _get_subnets_from_network(self, network):
        """Returns the 1 or 2 possible subnets for a engine network"""
        subnets = []

        # get dns information from network
        dns = []
        if network['dns1']:
            dns.append(network_model.IP(address=network['dns1'], type='dns'))
        if network['dns2']:
            dns.append(network_model.IP(address=network['dns2'], type='dns'))

        # if network contains v4 subnet
        if network['cidr']:
            subnet = network_model.Subnet(cidr=network['cidr'],
                                          gateway=network_model.IP(
                                              address=network['gateway'],
                                              type='gateway'))
            # if either dns address is v4, add it to subnet
            for ip in dns:
                if ip['version'] == 4:
                    subnet.add_dns(ip)

            # TODO(tr3buchet): add routes to subnet once it makes sense
            # create default route from gateway
            #route = network_model.Route(cidr=network['cidr'],
            #                             gateway=network['gateway'])
            #subnet.add_route(route)

            # store subnet for return
            subnets.append(subnet)

        # if network contains a v6 subnet
        if network['cidr_v6']:
            subnet = network_model.Subnet(cidr=network['cidr_v6'],
                                          gateway=network_model.IP(
                                              address=network['gateway_v6'],
                                              type='gateway'))
            # if either dns address is v6, add it to subnet
            for entry in dns:
                if entry['version'] == 6:
                    subnet.add_dns(entry)

            # TODO(tr3buchet): add routes to subnet once it makes sense
            # create default route from gateway
            #route = network_model.Route(cidr=network['cidr_v6'],
            #                             gateway=network['gateway_v6'])
            #subnet.add_route(route)

            # store subnet for return
            subnets.append(subnet)

        return subnets

    def _allocate_mac_addresses(self, context, instance_id, networks):
        """Generates mac addresses and creates vif rows in db for them."""
        for network in networks:
            self.add_virtual_interface(context, instance_id, network['id'])

    def add_virtual_interface(self, context, instance_id, network_id):
        vif = {'address': self.generate_mac_address(),
                   'instance_id': instance_id,
                   'network_id': network_id,
                   'uuid': str(utils.gen_uuid())}
        # try FLAG times to create a vif record with a unique mac_address
        for _ in xrange(FLAGS.create_unique_mac_address_attempts):
            try:
                return self.db.virtual_interface_create(context, vif)
            except exception.VirtualInterfaceCreateException:
                vif['address'] = self.generate_mac_address()
        else:
            self.db.virtual_interface_delete_by_instance(context,
                                                             instance_id)
            raise exception.VirtualInterfaceMacAddressException()

    def generate_mac_address(self):
        """Generate an Ethernet MAC address."""
        mac = [0x02, 0x16, 0x3e,
               random.randint(0x00, 0x7f),
               random.randint(0x00, 0xff),
               random.randint(0x00, 0xff)]
        return ':'.join(map(lambda x: "%02x" % x, mac))

    def add_fixed_ip_to_instance(self, context, instance_id, host, network_id):
        """Adds a fixed ip to an instance from specified network."""
        networks = [self.db.network_get(context, network_id)]
        self._allocate_fixed_ips(context, instance_id, host, networks)

    def remove_fixed_ip_from_instance(self, context, instance_id, address):
        """Removes a fixed ip from an instance from specified network."""
        fixed_ips = self.db.fixed_ip_get_by_instance(context, instance_id)
        for fixed_ip in fixed_ips:
            if fixed_ip['address'] == address:
                self.deallocate_fixed_ip(context, address)
                return
        raise exception.FixedIpNotFoundForSpecificInstance(
                                    instance_id=instance_id, ip=address)

    def allocate_fixed_ip(self, context, instance_id, network, **kwargs):
        """Gets a fixed ip from the pool."""
        # TODO(vish): when this is called by compute, we can associate compute
        #             with a network, or a cluster of computes with a network
        #             and use that network here with a method like
        #             network_get_by_compute_host
        address = None
        if network['cidr']:
            address = kwargs.get('address', None)
            if address:
                address = self.db.fixed_ip_associate(context,
                                                     address, instance_id,
                                                     network['id'])
            else:
                address = self.db.fixed_ip_associate_pool(context.elevated(),
                                                          network['id'],
                                                          instance_id)
            self._do_trigger_security_group_members_refresh_for_instance(
                                                                   instance_id)
            get_vif = self.db.virtual_interface_get_by_instance_and_network
            vif = get_vif(context, instance_id, network['id'])
            values = {'allocated': True,
                      'virtual_interface_id': vif['id']}
            self.db.fixed_ip_update(context, address, values)

        instance_ref = self.db.instance_get(context, instance_id)
        name = instance_ref['display_name']
        self.instance_dns_manager.create_entry(name, address,
                                               "type", FLAGS.instance_dns_zone)

        self._setup_network(context, network)
        return address

    def deallocate_fixed_ip(self, context, address, **kwargs):
        """Returns a fixed ip to the pool."""
        self.db.fixed_ip_update(context, address,
                                {'allocated': False,
                                 'virtual_interface_id': None})
        fixed_ip_ref = self.db.fixed_ip_get_by_address(context, address)
        instance_ref = fixed_ip_ref['instance']
        instance_id = instance_ref['id']
        self._do_trigger_security_group_members_refresh_for_instance(
                                                                   instance_id)

        for name in self.instance_dns_manager.get_entries_by_address(address):
            self.instance_dns_manager.delete_entry(name)

        if FLAGS.force_dhcp_release:
            dev = self.driver.get_dev(fixed_ip_ref['network'])
            vif = self.db.virtual_interface_get_by_instance_and_network(
                    context, instance_ref['id'], fixed_ip_ref['network']['id'])
            self.driver.release_dhcp(dev, address, vif['address'])

    def lease_fixed_ip(self, context, address):
        """Called by dhcp-bridge when ip is leased."""
        LOG.debug(_('Leased IP |%(address)s|'), locals(), context=context)
        fixed_ip = self.db.fixed_ip_get_by_address(context, address)
        instance = fixed_ip['instance']
        if not instance:
            raise exception.Error(_('IP %s leased that is not associated') %
                                  address)
        now = utils.utcnow()
        self.db.fixed_ip_update(context,
                                fixed_ip['address'],
                                {'leased': True,
                                 'updated_at': now})
        if not fixed_ip['allocated']:
            LOG.warn(_('IP |%s| leased that isn\'t allocated'), address,
                     context=context)

    def release_fixed_ip(self, context, address):
        """Called by dhcp-bridge when ip is released."""
        LOG.debug(_('Released IP |%(address)s|'), locals(), context=context)
        fixed_ip = self.db.fixed_ip_get_by_address(context, address)
        instance = fixed_ip['instance']
        if not instance:
            raise exception.Error(_('IP %s released that is not associated') %
                                  address)
        if not fixed_ip['leased']:
            LOG.warn(_('IP %s released that was not leased'), address,
                     context=context)
        self.db.fixed_ip_update(context,
                                fixed_ip['address'],
                                {'leased': False})
        if not fixed_ip['allocated']:
            self.db.fixed_ip_disassociate(context, address)
            # NOTE(vish): dhcp server isn't updated until next setup, this
            #             means there will stale entries in the conf file
            #             the code below will update the file if necessary
            if FLAGS.update_dhcp_on_disassociate:
                network_ref = self.db.fixed_ip_get_network(context, address)
                self._setup_network(context, network_ref)

    def create_networks(self, context, label, cidr, multi_host, num_networks,
                        network_size, cidr_v6, gateway, gateway_v6, bridge,
                        bridge_interface, dns1=None, dns2=None, **kwargs):
        """Create networks based on parameters."""
        # NOTE(jkoelker): these are dummy values to make sure iter works
        fixed_net_v4 = netaddr.IPNetwork('0/32')
        fixed_net_v6 = netaddr.IPNetwork('::0/128')
        subnets_v4 = []
        subnets_v6 = []

        subnet_bits = int(math.ceil(math.log(network_size, 2)))

        if cidr_v6:
            fixed_net_v6 = netaddr.IPNetwork(cidr_v6)
            prefixlen_v6 = 128 - subnet_bits
            subnets_v6 = fixed_net_v6.subnet(prefixlen_v6, count=num_networks)

        if cidr:
            fixed_net_v4 = netaddr.IPNetwork(cidr)
            prefixlen_v4 = 32 - subnet_bits
            subnets_v4 = list(fixed_net_v4.subnet(prefixlen_v4,
                                                  count=num_networks))

            # NOTE(jkoelker): This replaces the _validate_cidrs call and
            #                 prevents looping multiple times
            try:
                nets = self.db.network_get_all(context)
            except exception.NoNetworksFound:
                nets = []
            used_subnets = [netaddr.IPNetwork(net['cidr']) for net in nets]

            def find_next(subnet):
                next_subnet = subnet.next()
                while next_subnet in subnets_v4:
                    next_subnet = next_subnet.next()
                if next_subnet in fixed_net_v4:
                    return next_subnet

            for subnet in list(subnets_v4):
                if subnet in used_subnets:
                    next_subnet = find_next(subnet)
                    if next_subnet:
                        subnets_v4.remove(subnet)
                        subnets_v4.append(next_subnet)
                        subnet = next_subnet
                    else:
                        raise ValueError(_('cidr already in use'))
                for used_subnet in used_subnets:
                    if subnet in used_subnet:
                        msg = _('requested cidr (%(cidr)s) conflicts with '
                                'existing supernet (%(super)s)')
                        raise ValueError(msg % {'cidr': subnet,
                                                'super': used_subnet})
                    if used_subnet in subnet:
                        next_subnet = find_next(subnet)
                        if next_subnet:
                            subnets_v4.remove(subnet)
                            subnets_v4.append(next_subnet)
                            subnet = next_subnet
                        else:
                            msg = _('requested cidr (%(cidr)s) conflicts '
                                    'with existing smaller cidr '
                                    '(%(smaller)s)')
                            raise ValueError(msg % {'cidr': subnet,
                                                    'smaller': used_subnet})

        networks = []
        subnets = itertools.izip_longest(subnets_v4, subnets_v6)
        for index, (subnet_v4, subnet_v6) in enumerate(subnets):
            net = {}
            net['bridge'] = bridge
            net['bridge_interface'] = bridge_interface
            net['multi_host'] = multi_host

            net['dns1'] = dns1
            net['dns2'] = dns2

            net['project_id'] = kwargs.get('project_id')

            if num_networks > 1:
                net['label'] = '%s_%d' % (label, index)
            else:
                net['label'] = label

            if cidr and subnet_v4:
                net['cidr'] = str(subnet_v4)
                net['netmask'] = str(subnet_v4.netmask)
                net['gateway'] = gateway or str(subnet_v4[1])
                net['broadcast'] = str(subnet_v4.broadcast)
                net['dhcp_start'] = str(subnet_v4[2])

            if cidr_v6 and subnet_v6:
                net['cidr_v6'] = str(subnet_v6)
                if gateway_v6:
                    # use a pre-defined gateway if one is provided
                    net['gateway_v6'] = str(gateway_v6)
                else:
                    net['gateway_v6'] = str(subnet_v6[1])

                net['netmask_v6'] = str(subnet_v6._prefixlen)

            if kwargs.get('vpn', False):
                # this bit here is for vlan-manager
                del net['dns1']
                del net['dns2']
                vlan = kwargs['vlan_start'] + index
                net['vpn_private_address'] = str(subnet_v4[2])
                net['dhcp_start'] = str(subnet_v4[3])
                net['vlan'] = vlan
                net['bridge'] = 'br%s' % vlan

                # NOTE(vish): This makes ports unique across the cloud, a more
                #             robust solution would be to make them uniq per ip
                net['vpn_public_port'] = kwargs['vpn_start'] + index

            # None if network with cidr or cidr_v6 already exists
            network = self.db.network_create_safe(context, net)

            if not network:
                raise ValueError(_('Network already exists!'))
            else:
                networks.append(network)

            if network and cidr and subnet_v4:
                self._create_fixed_ips(context, network['id'])
        return networks

    def delete_network(self, context, fixed_range, uuid,
            require_disassociated=True):

        # Prefer uuid but we'll also take cidr for backwards compatibility
        if uuid:
            network = db.network_get_by_uuid(context.elevated(), uuid)
        elif fixed_range:
            network = db.network_get_by_cidr(context.elevated(), fixed_range)

        if require_disassociated and network.project_id is not None:
            raise ValueError(_('Network must be disassociated from project %s'
                               ' before delete' % network.project_id))
        db.network_delete_safe(context, network.id)

    @property
    def _bottom_reserved_ips(self):  # pylint: disable=R0201
        """Number of reserved ips at the bottom of the range."""
        return 2  # network, gateway

    @property
    def _top_reserved_ips(self):  # pylint: disable=R0201
        """Number of reserved ips at the top of the range."""
        return 1  # broadcast

    def _create_fixed_ips(self, context, network_id):
        """Create all fixed ips for network."""
        network = self.db.network_get(context, network_id)
        # NOTE(vish): Should these be properties of the network as opposed
        #             to properties of the manager class?
        bottom_reserved = self._bottom_reserved_ips
        top_reserved = self._top_reserved_ips
        project_net = netaddr.IPNetwork(network['cidr'])
        num_ips = len(project_net)
        ips = []
        for index in range(num_ips):
            address = str(project_net[index])
            if index < bottom_reserved or num_ips - index <= top_reserved:
                reserved = True
            else:
                reserved = False

            ips.append({'network_id': network_id,
                        'address': address,
                        'reserved': reserved})
        self.db.fixed_ip_bulk_create(context, ips)

    def _allocate_fixed_ips(self, context, instance_id, host, networks,
                            **kwargs):
        """Calls allocate_fixed_ip once for each network."""
        raise NotImplementedError()

    def _setup_network(self, context, network_ref):
        """Sets up network on this host."""
        raise NotImplementedError()

    def validate_networks(self, context, networks):
        """check if the networks exists and host
        is set to each network.
        """
        if networks is None or len(networks) == 0:
            return

        network_uuids = [uuid for (uuid, fixed_ip) in networks]

        self._get_networks_by_uuids(context, network_uuids)

        for network_uuid, address in networks:
            # check if the fixed IP address is valid and
            # it actually belongs to the network
            if address is not None:
                if not utils.is_valid_ipv4(address):
                    raise exception.FixedIpInvalid(address=address)

                fixed_ip_ref = self.db.fixed_ip_get_by_address(context,
                                                               address)
                if fixed_ip_ref['network']['uuid'] != network_uuid:
                    raise exception.FixedIpNotFoundForNetwork(address=address,
                                            network_uuid=network_uuid)
                if fixed_ip_ref['instance'] is not None:
                    raise exception.FixedIpAlreadyInUse(address=address)

    def _get_networks_by_uuids(self, context, network_uuids):
        return self.db.network_get_all_by_uuids(context, network_uuids)

    def get_vifs_by_instance(self, context, instance_id):
        """Returns the vifs associated with an instance"""
        vifs = self.db.virtual_interface_get_by_instance(context, instance_id)
        return [dict(vif.iteritems()) for vif in vifs]


class FlatManager(NetworkManager):
    """Basic network where no vlans are used.

    FlatManager does not do any bridge or vlan creation.  The user is
    responsible for setting up whatever bridges are specified when creating
    networks through engine-manage. This bridge needs to be created on all
    compute hosts.

    The idea is to create a single network for the host with a command like:
    engine-manage network create 192.168.0.0/24 1 256. Creating multiple
    networks for for one manager is currently not supported, but could be
    added by modifying allocate_fixed_ip and get_network to get the a network
    with new logic instead of network_get_by_bridge. Arbitrary lists of
    addresses in a single network can be accomplished with manual db editing.

    If flat_injected is True, the compute host will attempt to inject network
    config into the guest.  It attempts to modify /etc/network/interfaces and
    currently only works on debian based systems. To support a wider range of
    OSes, some other method may need to be devised to let the guest know which
    ip it should be using so that it can configure itself. Perhaps an attached
    disk or serial device with configuration info.

    Metadata forwarding must be handled by the gateway, and since engine does
    not do any setup in this mode, it must be done manually.  Requests to
    169.254.169.254 port 80 will need to be forwarded to the api server.

    """

    timeout_fixed_ips = False

    def _allocate_fixed_ips(self, context, instance_id, host, networks,
                            **kwargs):
        """Calls allocate_fixed_ip once for each network."""
        requested_networks = kwargs.get('requested_networks')
        for network in networks:
            address = None
            if requested_networks is not None:
                for address in (fixed_ip for (uuid, fixed_ip) in \
                              requested_networks if network['uuid'] == uuid):
                    break

            self.allocate_fixed_ip(context, instance_id,
                                   network, address=address)

    def deallocate_fixed_ip(self, context, address, **kwargs):
        """Returns a fixed ip to the pool."""
        super(FlatManager, self).deallocate_fixed_ip(context, address,
                                                     **kwargs)
        self.db.fixed_ip_disassociate(context, address)

    def _setup_network(self, context, network_ref):
        """Setup Network on this host."""
        net = {}
        net['injected'] = FLAGS.flat_injected
        self.db.network_update(context, network_ref['id'], net)


class FlatDHCPManager(RPCAllocateFixedIP, FloatingIP, NetworkManager):
    """Flat networking with dhcp.

    FlatDHCPManager will start up one dhcp server to give out addresses.
    It never injects network settings into the guest. It also manages bridges.
    Otherwise it behaves like FlatManager.

    """

    SHOULD_CREATE_BRIDGE = True

    def init_host(self):
        """Do any initialization that needs to be run if this is a
        standalone service.
        """
        self.driver.init_host()
        self.driver.ensure_metadata_ip()

        super(FlatDHCPManager, self).init_host()
        self.init_host_floating_ips()

        self.driver.metadata_forward()

    def _setup_network(self, context, network_ref):
        """Sets up network on this host."""
        network_ref['dhcp_server'] = self._get_dhcp_ip(context, network_ref)

        mac_address = self.generate_mac_address()
        dev = self.driver.plug(network_ref, mac_address)
        self.driver.initialize_gateway_device(dev, network_ref)

        if not FLAGS.fake_network:
            self.driver.update_dhcp(context, dev, network_ref)
            if(FLAGS.use_ipv6):
                self.driver.update_ra(context, dev, network_ref)
                gateway = utils.get_my_linklocal(dev)
                self.db.network_update(context, network_ref['id'],
                                       {'gateway_v6': gateway})


class VlanManager(RPCAllocateFixedIP, FloatingIP, NetworkManager):
    """Vlan network with dhcp.

    VlanManager is the most complicated.  It will create a host-managed
    vlan for each project.  Each project gets its own subnet.  The networks
    and associated subnets are created with engine-manage using a command like:
    engine-manage network create 10.0.0.0/8 3 16.  This will create 3 networks
    of 16 addresses from the beginning of the 10.0.0.0 range.

    A dhcp server is run for each subnet, so each project will have its own.
    For this mode to be useful, each project will need a vpn to access the
    instances in its subnet.

    """

    SHOULD_CREATE_BRIDGE = True
    SHOULD_CREATE_VLAN = True

    def init_host(self):
        """Do any initialization that needs to be run if this is a
        standalone service.
        """

        self.driver.init_host()
        self.driver.ensure_metadata_ip()

        NetworkManager.init_host(self)
        self.init_host_floating_ips()

        self.driver.metadata_forward()

    def allocate_fixed_ip(self, context, instance_id, network, **kwargs):
        """Gets a fixed ip from the pool."""
        if kwargs.get('vpn', None):
            address = network['vpn_private_address']
            self.db.fixed_ip_associate(context,
                                       address,
                                       instance_id,
                                       network['id'],
                                       reserved=True)
        else:
            address = kwargs.get('address', None)
            if address:
                address = self.db.fixed_ip_associate(context, address,
                                                     instance_id,
                                                     network['id'])
            else:
                address = self.db.fixed_ip_associate_pool(context,
                                                          network['id'],
                                                          instance_id)
            self._do_trigger_security_group_members_refresh_for_instance(
                                                                   instance_id)
        vif = self.db.virtual_interface_get_by_instance_and_network(context,
                                                                 instance_id,
                                                                 network['id'])
        values = {'allocated': True,
                  'virtual_interface_id': vif['id']}
        self.db.fixed_ip_update(context, address, values)
        self._setup_network(context, network)
        return address

    def add_network_to_project(self, context, project_id):
        """Force adds another network to a project."""
        self.db.network_associate(context, project_id, force=True)

    def _get_networks_for_instance(self, context, instance_id, project_id,
                                   requested_networks=None):
        """Determine which networks an instance should connect to."""
        # get networks associated with project
        if requested_networks is not None and len(requested_networks) != 0:
            network_uuids = [uuid for (uuid, fixed_ip) in requested_networks]
            networks = self.db.network_get_all_by_uuids(context,
                                                    network_uuids,
                                                    project_id)
        else:
            networks = self.db.project_get_networks(context, project_id)
        return networks

    def create_networks(self, context, **kwargs):
        """Create networks based on parameters."""
        # Check that num_networks + vlan_start is not > 4094, fixes lp708025
        if kwargs['num_networks'] + kwargs['vlan_start'] > 4094:
            raise ValueError(_('The sum between the number of networks and'
                               ' the vlan start cannot be greater'
                               ' than 4094'))

        # check that num networks and network size fits in fixed_net
        fixed_net = netaddr.IPNetwork(kwargs['cidr'])
        if len(fixed_net) < kwargs['num_networks'] * kwargs['network_size']:
            raise ValueError(_('The network range is not big enough to fit '
                  '%(num_networks)s. Network size is %(network_size)s') %
                  kwargs)

        NetworkManager.create_networks(self, context, vpn=True, **kwargs)

    def _setup_network(self, context, network_ref):
        """Sets up network on this host."""
        if not network_ref['vpn_public_address']:
            net = {}
            address = FLAGS.vpn_ip
            net['vpn_public_address'] = address
            network_ref = db.network_update(context, network_ref['id'], net)
        else:
            address = network_ref['vpn_public_address']
        network_ref['dhcp_server'] = self._get_dhcp_ip(context, network_ref)

        mac_address = self.generate_mac_address()
        dev = self.driver.plug(network_ref, mac_address)
        self.driver.initialize_gateway_device(dev, network_ref)

        # NOTE(vish): only ensure this forward if the address hasn't been set
        #             manually.
        if address == FLAGS.vpn_ip and hasattr(self.driver,
                                               "ensure_vpn_forward"):
            self.driver.ensure_vpn_forward(FLAGS.vpn_ip,
                                            network_ref['vpn_public_port'],
                                            network_ref['vpn_private_address'])
        if not FLAGS.fake_network:
            self.driver.update_dhcp(context, dev, network_ref)
            if(FLAGS.use_ipv6):
                self.driver.update_ra(context, dev, network_ref)
                gateway = utils.get_my_linklocal(dev)
                self.db.network_update(context, network_ref['id'],
                                       {'gateway_v6': gateway})

    def _get_networks_by_uuids(self, context, network_uuids):
        return self.db.network_get_all_by_uuids(context, network_uuids,
                                                     context.project_id)

    @property
    def _bottom_reserved_ips(self):
        """Number of reserved ips at the bottom of the range."""
        return super(VlanManager, self)._bottom_reserved_ips + 1  # vpn server

    @property
    def _top_reserved_ips(self):
        """Number of reserved ips at the top of the range."""
        parent_reserved = super(VlanManager, self)._top_reserved_ips
        return parent_reserved + FLAGS.cnt_vpn_clients

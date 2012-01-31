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


import json
import operator

import engine.scheduler
from engine.scheduler.filters import abstract_filter


class JsonFilter(abstract_filter.AbstractHostFilter):
    """Host Filter to allow simple JSON-based grammar for
    selecting hosts.
    """
    def _op_compare(self, args, op):
        """Returns True if the specified operator can successfully
        compare the first item in the args with all the rest. Will
        return False if only one item is in the list.
        """
        if len(args) < 2:
            return False
        if op is operator.contains:
            bad = not args[0] in args[1:]
        else:
            bad = [arg for arg in args[1:]
                    if not op(args[0], arg)]
        return not bool(bad)

    def _equals(self, args):
        """First term is == all the other terms."""
        return self._op_compare(args, operator.eq)

    def _less_than(self, args):
        """First term is < all the other terms."""
        return self._op_compare(args, operator.lt)

    def _greater_than(self, args):
        """First term is > all the other terms."""
        return self._op_compare(args, operator.gt)

    def _in(self, args):
        """First term is in set of remaining terms"""
        return self._op_compare(args, operator.contains)

    def _less_than_equal(self, args):
        """First term is <= all the other terms."""
        return self._op_compare(args, operator.le)

    def _greater_than_equal(self, args):
        """First term is >= all the other terms."""
        return self._op_compare(args, operator.ge)

    def _not(self, args):
        """Flip each of the arguments."""
        return [not arg for arg in args]

    def _or(self, args):
        """True if any arg is True."""
        return any(args)

    def _and(self, args):
        """True if all args are True."""
        return all(args)

    commands = {
        '=': _equals,
        '<': _less_than,
        '>': _greater_than,
        'in': _in,
        '<=': _less_than_equal,
        '>=': _greater_than_equal,
        'not': _not,
        'or': _or,
        'and': _and,
    }

    def instance_type_to_filter(self, instance_type):
        """Convert instance_type into JSON filter object."""
        required_ram = instance_type['memory_mb']
        required_disk = instance_type['local_gb']
        query = ['and',
                ['>=', '$compute.host_memory_free', required_ram],
                ['>=', '$compute.disk_available', required_disk]]
        return json.dumps(query)

    def _parse_string(self, string, host, hostinfo):
        """Strings prefixed with $ are capability lookups in the
        form '$service.capability[.subcap*]'.
        """
        if not string:
            return None
        if not string.startswith("$"):
            return string

        path = string[1:].split(".")
        services = dict(compute=hostinfo.compute, network=hostinfo.network,
                        volume=hostinfo.volume)
        service = services.get(path[0], None)
        if not service:
            return None
        for item in path[1:]:
            service = service.get(item, None)
            if not service:
                return None
        return service

    def _process_filter(self, query, host, hostinfo):
        """Recursively parse the query structure."""
        if not query:
            return True
        cmd = query[0]
        method = self.commands[cmd]
        cooked_args = []
        for arg in query[1:]:
            if isinstance(arg, list):
                arg = self._process_filter(arg, host, hostinfo)
            elif isinstance(arg, basestring):
                arg = self._parse_string(arg, host, hostinfo)
            if arg is not None:
                cooked_args.append(arg)
        result = method(self, cooked_args)
        return result

    def filter_hosts(self, host_list, query, options):
        """Return a list of hosts that can fulfill the requirements
        specified in the query.
        """
        expanded = json.loads(query)
        filtered_hosts = []
        for host, hostinfo in host_list:
            if not hostinfo:
                continue
            if hostinfo.compute and not hostinfo.compute.get("enabled", True):
                # Host is disabled
                continue
            result = self._process_filter(expanded, host, hostinfo)
            if isinstance(result, list):
                # If any succeeded, include the host
                result = any(result)
            if result:
                filtered_hosts.append((host, hostinfo))
        return filtered_hosts

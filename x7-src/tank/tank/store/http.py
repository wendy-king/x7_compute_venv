# vim: tabstop=4 shiftwidth=4 softtabstop=4

# Copyright 2010 X7, LLC
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

import httplib
import urlparse

from tank.common import exception
import tank.store.base
import tank.store.location


class StoreLocation(tank.store.location.StoreLocation):

    """Class describing an HTTP(S) URI"""

    def process_specs(self):
        self.scheme = self.specs.get('scheme', 'http')
        self.netloc = self.specs['netloc']
        self.user = self.specs.get('user')
        self.password = self.specs.get('password')
        self.path = self.specs.get('path')

    def _get_credstring(self):
        if self.user:
            return '%s:%s@' % (self.user, self.password)
        return ''

    def get_uri(self):
        return "%s://%s%s%s" % (
            self.scheme,
            self._get_credstring(),
            self.netloc,
            self.path)

    def parse_uri(self, uri):
        """
        Parse URLs. This method fixes an issue where credentials specified
        in the URL are interpreted differently in Python 2.6.1+ than prior
        versions of Python.
        """
        pieces = urlparse.urlparse(uri)
        assert pieces.scheme in ('https', 'http')
        self.scheme = pieces.scheme
        netloc = pieces.netloc
        path = pieces.path
        try:
            if '@' in netloc:
                creds, netloc = netloc.split('@')
            else:
                creds = None
        except ValueError:
            # Python 2.6.1 compat
            # see lp659445 and Python issue7904
            if '@' in path:
                creds, path = path.split('@')
            else:
                creds = None
        if creds:
            try:
                self.user, self.password = creds.split(':')
            except ValueError:
                reason = (_("Credentials '%s' not well-formatted.")
                          % "".join(creds))
                raise exception.BadStoreUri(uri, reason)
        else:
            self.user = None
        if netloc == '':
            reason = _("No address specified in HTTP URL")
            raise exception.BadStoreUri(uri, reason)
        self.netloc = netloc
        self.path = path


def http_response_iterator(conn, response, size):
    """
    Return an iterator for a file-like object.

    :param conn: HTTP(S) Connection
    :param response: httplib.HTTPResponse object
    :param size: Chunk size to iterate with
    """
    chunk = response.read(size)
    while chunk:
        yield chunk
        chunk = response.read(size)
    conn.close()


class Store(tank.store.base.Store):

    """An implementation of the HTTP(S) Backend Adapter"""

    def get(self, location):
        """
        Takes a `tank.store.location.Location` object that indicates
        where to find the image file, and returns a tuple of generator
        (for reading the image file) and image_size

        :param location `tank.store.location.Location` object, supplied
                        from tank.store.location.get_location_from_uri()
        """
        loc = location.store_location

        conn_class = self._get_conn_class(loc)
        conn = conn_class(loc.netloc)
        conn.request("GET", loc.path, "", {})
        resp = conn.getresponse()

        content_length = resp.getheader('content-length', 0)
        iterator = http_response_iterator(conn, resp, self.CHUNKSIZE)

        return (iterator, content_length)

    def _get_conn_class(self, loc):
        """
        Returns connection class for accessing the resource. Useful
        for dependency injection and stubouts in testing...
        """
        return {'http': httplib.HTTPConnection,
                'https': httplib.HTTPSConnection}[loc.scheme]


tank.store.register_store(__name__, ['http', 'https'])

# vim: tabstop=4 shiftwidth=4 softtabstop=4

# Copyright 2010-2011 X7, LLC
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

"""Storage backend for CHASE"""

from __future__ import absolute_import

import hashlib
import httplib
import logging
import math
import tempfile
import urlparse

from tank.common import cfg
from tank.common import exception
import tank.store
import tank.store.base
import tank.store.location

try:
    from chase.common import client as chase_client
except ImportError:
    pass

DEFAULT_CONTAINER = 'tank'
DEFAULT_LARGE_OBJECT_SIZE = 5 * 1024  # 5GB
DEFAULT_LARGE_OBJECT_CHUNK_SIZE = 200  # 200M
ONE_MB = 1000 * 1024

logger = logging.getLogger('tank.store.chase')


class StoreLocation(tank.store.location.StoreLocation):

    """
    Class describing a Chase URI. A Chase URI can look like any of
    the following:

        chase://user:pass@authurl.com/container/obj-id
        chase://account:user:pass@authurl.com/container/obj-id
        chase+http://user:pass@authurl.com/container/obj-id
        chase+https://user:pass@authurl.com/container/obj-id

    The chase+http:// URIs indicate there is an HTTP authentication URL.
    The default for Chase is an HTTPS authentication URL, so chase:// and
    chase+https:// are the same...
    """

    def process_specs(self):
        self.scheme = self.specs.get('scheme', 'chase+https')
        self.user = self.specs.get('user')
        self.key = self.specs.get('key')
        self.authurl = self.specs.get('authurl')
        self.container = self.specs.get('container')
        self.obj = self.specs.get('obj')

    def _get_credstring(self):
        if self.user:
            return '%s:%s@' % (self.user, self.key)
        return ''

    def get_uri(self):
        authurl = self.authurl
        if authurl.startswith('http://'):
            authurl = authurl[7:]
        elif authurl.startswith('https://'):
            authurl = authurl[8:]

        credstring = self._get_credstring()
        authurl = authurl.strip('/')
        container = self.container.strip('/')
        obj = self.obj.strip('/')

        return '%s://%s%s/%s/%s' % (self.scheme, credstring, authurl,
                                    container, obj)

    def parse_uri(self, uri):
        """
        Parse URLs. This method fixes an issue where credentials specified
        in the URL are interpreted differently in Python 2.6.1+ than prior
        versions of Python. It also deals with the peculiarity that new-style
        Chase URIs have where a username can contain a ':', like so:

            chase://account:user:pass@authurl.com/container/obj
        """
        # Make sure that URIs that contain multiple schemes, such as:
        # chase://user:pass@http://authurl.com/v1/container/obj
        # are immediately rejected.
        if uri.count('://') != 1:
            reason = _(
                    "URI cannot contain more than one occurrence of a scheme."
                    "If you have specified a URI like "
                    "chase://user:pass@http://authurl.com/v1/container/obj"
                    ", you need to change it to use the chase+http:// scheme, "
                    "like so: "
                    "chase+http://user:pass@authurl.com/v1/container/obj"
                    )
            raise exception.BadStoreUri(uri, reason)

        pieces = urlparse.urlparse(uri)
        assert pieces.scheme in ('chase', 'chase+http', 'chase+https')
        self.scheme = pieces.scheme
        netloc = pieces.netloc
        path = pieces.path.lstrip('/')
        if netloc != '':
            # > Python 2.6.1
            if '@' in netloc:
                creds, netloc = netloc.split('@')
            else:
                creds = None
        else:
            # Python 2.6.1 compat
            # see lp659445 and Python issue7904
            if '@' in path:
                creds, path = path.split('@')
            else:
                creds = None
            netloc = path[0:path.find('/')].strip('/')
            path = path[path.find('/'):].strip('/')
        if creds:
            cred_parts = creds.split(':')

            # User can be account:user, in which case cred_parts[0:2] will be
            # the account and user. Combine them into a single username of
            # account:user
            if len(cred_parts) == 1:
                reason = (_("Badly formed credentials '%(creds)s' in Chase "
                            "URI") % locals())
                raise exception.BadStoreUri(uri, reason)
            elif len(cred_parts) == 3:
                user = ':'.join(cred_parts[0:2])
            else:
                user = cred_parts[0]
            key = cred_parts[-1]
            self.user = user
            self.key = key
        else:
            self.user = None
        path_parts = path.split('/')
        try:
            self.obj = path_parts.pop()
            self.container = path_parts.pop()
            if not netloc.startswith('http'):
                # push hostname back into the remaining to build full authurl
                path_parts.insert(0, netloc)
                self.authurl = '/'.join(path_parts)
        except IndexError:
            reason = _("Badly formed Chase URI")
            raise exception.BadStoreUri(uri, reason)

    @property
    def chase_auth_url(self):
        """
        Creates a fully-qualified auth url that the Chase client library can
        use. The scheme for the auth_url is determined using the scheme
        included in the `location` field.

        HTTPS is assumed, unless 'chase+http' is specified.
        """
        if self.scheme in ('chase+https', 'chase'):
            auth_scheme = 'https://'
        else:
            auth_scheme = 'http://'

        full_url = ''.join([auth_scheme, self.authurl])
        return full_url


class Store(tank.store.base.Store):
    """An implementation of the chase backend adapter."""

    EXAMPLE_URL = "chase://<USER>:<KEY>@<AUTH_ADDRESS>/<CONTAINER>/<FILE>"

    CHUNKSIZE = 65536

    opts = [
        cfg.BoolOpt('chase_enable_snet', default=False),
        cfg.StrOpt('chase_store_auth_address'),
        cfg.StrOpt('chase_store_user'),
        cfg.StrOpt('chase_store_key'),
        cfg.StrOpt('chase_store_container',
                   default=DEFAULT_CONTAINER),
        cfg.IntOpt('chase_store_large_object_size',
                   default=DEFAULT_LARGE_OBJECT_SIZE),
        cfg.IntOpt('chase_store_large_object_chunk_size',
                   default=DEFAULT_LARGE_OBJECT_CHUNK_SIZE),
        cfg.BoolOpt('chase_store_create_container_on_put', default=False),
        ]

    def configure(self):
        self.conf.register_opts(self.opts)
        self.snet = self.conf.chase_enable_snet

    def configure_add(self):
        """
        Configure the Store to use the stored configuration options
        Any store that needs special configuration should implement
        this method. If the store was not able to successfully configure
        itself, it should raise `exception.BadStoreConfiguration`
        """
        self.auth_address = self._option_get('chase_store_auth_address')
        self.user = self._option_get('chase_store_user')
        self.key = self._option_get('chase_store_key')
        self.container = self.conf.chase_store_container
        try:
            # The config file has chase_store_large_object_*size in MB, but
            # internally we store it in bytes, since the image_size parameter
            # passed to add() is also in bytes.
            self.large_object_size = \
                self.conf.chase_store_large_object_size * ONE_MB
            self.large_object_chunk_size = \
                self.conf.chase_store_large_object_chunk_size * ONE_MB
        except cfg.ConfigFileValueError, e:
            reason = _("Error in configuration conf: %s") % e
            logger.error(reason)
            raise exception.BadStoreConfiguration(store_name="chase",
                                                  reason=reason)

        self.scheme = 'chase+https'
        if self.auth_address.startswith('http://'):
            self.scheme = 'chase+http'
            self.full_auth_address = self.auth_address
        elif self.auth_address.startswith('https://'):
            self.full_auth_address = self.auth_address
        else:  # Defaults https
            self.full_auth_address = 'https://' + self.auth_address

    def get(self, location):
        """
        Takes a `tank.store.location.Location` object that indicates
        where to find the image file, and returns a tuple of generator
        (for reading the image file) and image_size

        :param location `tank.store.location.Location` object, supplied
                        from tank.store.location.get_location_from_uri()
        :raises `tank.exception.NotFound` if image does not exist
        """
        loc = location.store_location
        chase_conn = self._make_chase_connection(
            auth_url=loc.chase_auth_url, user=loc.user, key=loc.key)

        try:
            (resp_headers, resp_body) = chase_conn.get_object(
                container=loc.container, obj=loc.obj,
                resp_chunk_size=self.CHUNKSIZE)
        except chase_client.ClientException, e:
            if e.http_status == httplib.NOT_FOUND:
                uri = location.get_store_uri()
                raise exception.NotFound(_("Chase could not find image at "
                                         "uri %(uri)s") % locals())
            else:
                raise

        #if expected_size:
        #    obj_size = int(resp_headers['content-length'])
        #    if  obj_size != expected_size:
        #        raise tank.store.BackendException(
        #            "Expected %s byte file, Chase has %s bytes" %
        #            (expected_size, obj_size))

        return (resp_body, resp_headers.get('content-length'))

    def _make_chase_connection(self, auth_url, user, key):
        """
        Creates a connection using the Chase client library.
        """
        snet = self.snet
        logger.debug(_("Creating Chase connection with "
                     "(auth_address=%(auth_url)s, user=%(user)s, "
                     "snet=%(snet)s)") % locals())
        return chase_client.Connection(
            authurl=auth_url, user=user, key=key, snet=snet)

    def _option_get(self, param):
        result = getattr(self.conf, param)
        if not result:
            reason = (_("Could not find %(param)s in configuration "
                        "options.") % locals())
            logger.error(reason)
            raise exception.BadStoreConfiguration(store_name="chase",
                                                  reason=reason)
        return result

    def add(self, image_id, image_file, image_size):
        """
        Stores an image file with supplied identifier to the backend
        storage system and returns an `tank.store.ImageAddResult` object
        containing information about the stored image.

        :param image_id: The opaque image identifier
        :param image_file: The image data to write, as a file-like object
        :param image_size: The size of the image data to write, in bytes

        :retval `tank.store.ImageAddResult` object
        :raises `tank.common.exception.Duplicate` if the image already
                existed

        Chase writes the image data using the scheme:
            ``chase://<USER>:<KEY>@<AUTH_ADDRESS>/<CONTAINER>/<ID>`
        where:
            <USER> = ``chase_store_user``
            <KEY> = ``chase_store_key``
            <AUTH_ADDRESS> = ``chase_store_auth_address``
            <CONTAINER> = ``chase_store_container``
            <ID> = The id of the image being added

        :note Chase auth URLs by default use HTTPS. To specify an HTTP
              auth URL, you can specify http://someurl.com for the
              chase_store_auth_address config option

        :note Chase cannot natively/transparently handle objects >5GB
              in size. So, if the image is greater than 5GB, we write
              chunks of image data to Chase and then write an manifest
              to Chase that contains information about the chunks.
              This same chunking process is used by default for images
              of an unknown size, as pushing them directly to chase would
              fail if the image turns out to be greater than 5GB.
        """
        chase_conn = self._make_chase_connection(
            auth_url=self.full_auth_address, user=self.user, key=self.key)

        create_container_if_missing(self.container, chase_conn, self.conf)

        obj_name = str(image_id)
        location = StoreLocation({'scheme': self.scheme,
                                  'container': self.container,
                                  'obj': obj_name,
                                  'authurl': self.auth_address,
                                  'user': self.user,
                                  'key': self.key})

        logger.debug(_("Adding image object '%(obj_name)s' "
                       "to Chase") % locals())
        try:
            if image_size > 0 and image_size < self.large_object_size:
                # Image size is known, and is less than large_object_size.
                # Send to Chase with regular PUT.
                obj_etag = chase_conn.put_object(self.container, obj_name,
                                                 image_file,
                                                 content_length=image_size)
            else:
                # Write the image into Chase in chunks.
                chunk_id = 1
                if image_size > 0:
                    total_chunks = str(int(
                        math.ceil(float(image_size) /
                                  float(self.large_object_chunk_size))))
                else:
                    # image_size == 0 is when we don't know the size
                    # of the image. This can occur with older clients
                    # that don't inspect the payload size.
                    logger.debug(_("Cannot determine image size. Adding as a "
                                   "segmented object to Chase."))
                    total_chunks = '?'

                checksum = hashlib.md5()
                combined_chunks_size = 0
                while True:
                    chunk_size = self.large_object_chunk_size
                    if image_size == 0:
                        content_length = None
                    else:
                        left = image_size - combined_chunks_size
                        if left == 0:
                            break
                        if chunk_size > left:
                            chunk_size = left
                        content_length = chunk_size

                    chunk_name = "%s-%05d" % (obj_name, chunk_id)
                    reader = ChunkReader(image_file, checksum, chunk_size)
                    chunk_etag = chase_conn.put_object(
                        self.container, chunk_name, reader,
                        content_length=content_length)
                    bytes_read = reader.bytes_read
                    logger.debug(_("Wrote chunk %(chunk_id)d/"
                                   "%(total_chunks)s of length %(bytes_read)d "
                                   "to Chase returning MD5 of content: "
                                   "%(chunk_etag)s")
                                 % locals())

                    if bytes_read == 0:
                        # Delete the last chunk, because it's of zero size.
                        # This will happen if image_size == 0.
                        logger.debug(_("Deleting final zero-length chunk"))
                        chase_conn.delete_object(self.container, chunk_name)
                        break

                    chunk_id += 1
                    combined_chunks_size += bytes_read

                # In the case we have been given an unknown image size,
                # set the image_size to the total size of the combined chunks.
                if image_size == 0:
                    image_size = combined_chunks_size

                # Now we write the object manifest and return the
                # manifest's etag...
                manifest = "%s/%s" % (self.container, obj_name)
                headers = {'ETag': hashlib.md5("").hexdigest(),
                           'X-Object-Manifest': manifest}

                # The ETag returned for the manifest is actually the
                # MD5 hash of the concatenated checksums of the strings
                # of each chunk...so we ignore this result in favour of
                # the MD5 of the entire image file contents, so that
                # users can verify the image file contents accordingly
                _ignored = chase_conn.put_object(self.container, obj_name,
                                                 None, headers=headers)
                obj_etag = checksum.hexdigest()

            # NOTE: We return the user and key here! Have to because
            # location is used by the API server to return the actual
            # image data. We *really* should consider NOT returning
            # the location attribute from GET /images/<ID> and
            # GET /images/details

            return (location.get_uri(), image_size, obj_etag)
        except chase_client.ClientException, e:
            if e.http_status == httplib.CONFLICT:
                raise exception.Duplicate(_("Chase already has an image at "
                                          "location %s") % location.get_uri())
            msg = (_("Failed to add object to Chase.\n"
                   "Got error from Chase: %(e)s") % locals())
            logger.error(msg)
            raise tank.store.BackendException(msg)

    def delete(self, location):
        """
        Takes a `tank.store.location.Location` object that indicates
        where to find the image file to delete

        :location `tank.store.location.Location` object, supplied
                  from tank.store.location.get_location_from_uri()

        :raises NotFound if image does not exist
        """
        loc = location.store_location
        chase_conn = self._make_chase_connection(
            auth_url=loc.chase_auth_url, user=loc.user, key=loc.key)

        try:
            # We request the manifest for the object. If one exists,
            # that means the object was uploaded in chunks/segments,
            # and we need to delete all the chunks as well as the
            # manifest.
            manifest = None
            try:
                headers = chase_conn.head_object(loc.container, loc.obj)
                manifest = headers.get('x-object-manifest')
            except chase_client.ClientException, e:
                if e.http_status != httplib.NOT_FOUND:
                    raise
            if manifest:
                # Delete all the chunks before the object manifest itself
                obj_container, obj_prefix = manifest.split('/', 1)
                for segment in chase_conn.get_container(obj_container,
                                                        prefix=obj_prefix)[1]:
                    # TODO(jaypipes): This would be an easy area to parallelize
                    # since we're simply sending off parallelizable requests
                    # to Chase to delete stuff. It's not like we're going to
                    # be hogging up network or file I/O here...
                    chase_conn.delete_object(obj_container, segment['name'])

            else:
                chase_conn.delete_object(loc.container, loc.obj)

        except chase_client.ClientException, e:
            if e.http_status == httplib.NOT_FOUND:
                uri = location.get_store_uri()
                raise exception.NotFound(_("Chase could not find image at "
                                         "uri %(uri)s") % locals())
            else:
                raise


class ChunkReader(object):
    def __init__(self, fd, checksum, total):
        self.fd = fd
        self.checksum = checksum
        self.total = total
        self.bytes_read = 0

    def read(self, i):
        left = self.total - self.bytes_read
        if i > left:
            i = left
        result = self.fd.read(i)
        self.bytes_read += len(result)
        self.checksum.update(result)
        return result


def create_container_if_missing(container, chase_conn, conf):
    """
    Creates a missing container in Chase if the
    ``chase_store_create_container_on_put`` option is set.

    :param container: Name of container to create
    :param chase_conn: Connection to Chase
    :param conf: Option mapping
    """
    try:
        chase_conn.head_container(container)
    except chase_client.ClientException, e:
        if e.http_status == httplib.NOT_FOUND:
            if conf.chase_store_create_container_on_put:
                try:
                    chase_conn.put_container(container)
                except ClientException, e:
                    msg = _("Failed to add container to Chase.\n"
                           "Got error from Chase: %(e)s") % locals()
                    raise tank.store.BackendException(msg)
            else:
                msg = (_("The container %(container)s does not exist in "
                       "Chase. Please set the "
                       "chase_store_create_container_on_put option"
                       "to add container to Chase automatically.")
                       % locals())
                raise tank.store.BackendException(msg)
        else:
            raise


tank.store.register_store(__name__, ['chase', 'chase+http', 'chase+https'])

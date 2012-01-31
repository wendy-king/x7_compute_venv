# vim: tabstop=4 shiftwidth=4 softtabstop=4

# Copyright 2010 X7 LLC.
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

import datetime

import webob
import webob.dec
import webob.request

from tank import client as tank_client

import engine.api.x7.v2.auth
from engine.api import auth as api_auth
from engine.api.x7 import v2
from engine.api.x7.v2 import auth
from engine.api.x7.v2 import extensions
from engine.api.x7.v2 import limits
from engine.api.x7.v2 import urlmap
from engine.api.x7.v2 import versions
from engine.api.x7 import wsgi as os_wsgi
from engine.auth.manager import User, Project
from engine.compute import instance_types
from engine.compute import vm_states
from engine import context
from engine.db.sqlalchemy import models
from engine import exception as exc
import engine.image.fake
from engine.tests.tank import stubs as tank_stubs
from engine import utils
from engine import wsgi


class Context(object):
    pass


class FakeRouter(wsgi.Router):
    def __init__(self):
        pass

    @webob.dec.wsgify
    def __call__(self, req):
        res = webob.Response()
        res.status = '200'
        res.headers['X-Test-Success'] = 'True'
        return res


def fake_auth_init(self, application):
    self.db = FakeAuthDatabase()
    self.context = Context()
    self.auth = FakeAuthManager()
    self.application = application


@webob.dec.wsgify
def fake_wsgi(self, req):
    return self.application


def wsgi_app(inner_app_v2=None, fake_auth=True, fake_auth_context=None,
        serialization=os_wsgi.LazySerializationMiddleware,
        use_no_auth=False):
    if not inner_app_v2:
        inner_app_v2 = v2.APIRouter()

    if fake_auth:
        if fake_auth_context is not None:
            ctxt = fake_auth_context
        else:
            ctxt = context.RequestContext('fake', 'fake', auth_token=True)
        api_v2 = v2.FaultWrapper(api_auth.InjectContext(ctxt,
              limits.RateLimitingMiddleware(
                  serialization(
                      extensions.ExtensionMiddleware(inner_app_v2)))))
    elif use_no_auth:
        api_v2 = v2.FaultWrapper(auth.NoAuthMiddleware(
              limits.RateLimitingMiddleware(
                  serialization(
                      extensions.ExtensionMiddleware(inner_app_v2)))))
    else:
        api_v2 = v2.FaultWrapper(auth.AuthMiddleware(
              limits.RateLimitingMiddleware(
                  serialization(
                      extensions.ExtensionMiddleware(inner_app_v2)))))

    mapper = urlmap.URLMap()
    mapper['/v2'] = api_v2
    mapper['/v1.1'] = api_v2
    mapper['/'] = v2.FaultWrapper(versions.Versions())
    return mapper


def stub_out_key_pair_funcs(stubs, have_key_pair=True):
    def key_pair(context, user_id):
        return [dict(name='key', public_key='public_key')]

    def one_key_pair(context, user_id, name):
        if name == 'key':
            return dict(name='key', public_key='public_key')
        else:
            raise exc.KeypairNotFound(user_id=user_id, name=name)

    def no_key_pair(context, user_id):
        return []

    if have_key_pair:
        stubs.Set(engine.db, 'key_pair_get_all_by_user', key_pair)
        stubs.Set(engine.db, 'key_pair_get', one_key_pair)
    else:
        stubs.Set(engine.db, 'key_pair_get_all_by_user', no_key_pair)


def stub_out_image_service(stubs):
    def fake_get_image_service(context, image_href):
        return (engine.image.fake.FakeImageService(), image_href)
    stubs.Set(engine.image, 'get_image_service', fake_get_image_service)
    stubs.Set(engine.image, 'get_default_image_service',
        lambda: engine.image.fake.FakeImageService())


def stub_out_auth(stubs):
    def fake_auth_init(self, app):
        self.application = app

    stubs.Set(engine.api.x7.v2.auth.AuthMiddleware,
        '__init__', fake_auth_init)
    stubs.Set(engine.api.x7.v2.auth.AuthMiddleware,
        '__call__', fake_wsgi)


def stub_out_rate_limiting(stubs):
    def fake_rate_init(self, app):
        super(limits.RateLimitingMiddleware, self).__init__(app)
        self.application = app

    stubs.Set(engine.api.x7.v2.limits.RateLimitingMiddleware,
        '__init__', fake_rate_init)

    stubs.Set(engine.api.x7.v2.limits.RateLimitingMiddleware,
        '__call__', fake_wsgi)


def stub_out_networking(stubs):
    def get_my_ip():
        return '127.0.0.1'
    stubs.Set(engine.flags, '_get_my_ip', get_my_ip)


class stub_out_compute_api_snapshot(object):

    def __init__(self, stubs):
        self.stubs = stubs
        self.extra_props_last_call = None
        stubs.Set(engine.compute.API, 'snapshot', self.snapshot)

    def snapshot(self, context, instance, name, extra_properties=None):
        self.extra_props_last_call = extra_properties
        return dict(id='123', status='ACTIVE', name=name,
                    properties=extra_properties)


class stub_out_compute_api_backup(object):

    def __init__(self, stubs):
        self.stubs = stubs
        self.extra_props_last_call = None
        stubs.Set(engine.compute.API, 'backup', self.backup)

    def backup(self, context, instance, name, backup_type, rotation,
               extra_properties=None):
        self.extra_props_last_call = extra_properties
        props = dict(backup_type=backup_type,
                     rotation=rotation)
        props.update(extra_properties or {})
        return dict(id='123', status='ACTIVE', name=name, properties=props)


def stub_out_nw_api_get_instance_nw_info(stubs, func=None):
    def get_instance_nw_info(self, context, instance):
        return [(None, {'label': 'public',
                         'ips': [{'ip': '192.168.0.3'}],
                         'ip6s': []})]

    if func is None:
        func = get_instance_nw_info
    stubs.Set(engine.network.API, 'get_instance_nw_info', func)


def stub_out_nw_api_get_floating_ips_by_fixed_address(stubs, func=None):
    def get_floating_ips_by_fixed_address(self, context, fixed_ip):
        return ['1.2.3.4']

    if func is None:
        func = get_floating_ips_by_fixed_address
    stubs.Set(engine.network.API, 'get_floating_ips_by_fixed_address', func)


def stub_out_nw_api(stubs, cls=None, private=None, publics=None):
    if not private:
        private = '192.168.0.3'
    if not publics:
        publics = ['1.2.3.4']

    class Fake:
        def get_instance_nw_info(*args, **kwargs):
            return [(None, {'label': 'private',
                            'ips': [{'ip': private}]})]

        def get_floating_ips_by_fixed_address(*args, **kwargs):
            return publics

    if cls is None:
        cls = Fake
    stubs.Set(engine.network, 'API', cls)


def _make_image_fixtures():
    NOW_TANK_FORMAT = "2010-10-11T10:30:22"

    image_id = 123
    base_attrs = {'deleted': False}

    fixtures = []

    def add_fixture(**kwargs):
        kwargs.update(base_attrs)
        fixtures.append(kwargs)

    # Public image
    add_fixture(id=image_id, name='public image', is_public=True,
                status='active', properties={'key1': 'value1'},
                min_ram="128", min_disk="10")
    image_id += 1

    # Snapshot for User 1
    uuid = 'aa640691-d1a7-4a67-9d3c-d35ee6b3cc74'
    server_ref = 'http://localhost/v2/servers/' + uuid
    snapshot_properties = {'instance_ref': server_ref, 'user_id': 'fake'}
    for status in ('queued', 'saving', 'active', 'killed',
                   'deleted', 'pending_delete'):
        add_fixture(id=image_id, name='%s snapshot' % status,
                    is_public=False, status=status,
                    properties=snapshot_properties)
        image_id += 1

    # Image without a name
    add_fixture(id=image_id, is_public=True, status='active', properties={})

    return fixtures


def stub_out_tank_add_image(stubs, sent_to_tank):
    """
    We return the metadata sent to tank by modifying the sent_to_tank dict
    in place.
    """
    orig_add_image = tank_client.Client.add_image

    def fake_add_image(context, metadata, data=None):
        sent_to_tank['metadata'] = metadata
        sent_to_tank['data'] = data
        return orig_add_image(metadata, data)

    stubs.Set(tank_client.Client, 'add_image', fake_add_image)


def stub_out_tank(stubs):
    def fake_get_image_service():
        client = tank_stubs.StubTankClient(_make_image_fixtures())
        return engine.image.tank.TankImageService(client)
    stubs.Set(engine.image, 'get_default_image_service', fake_get_image_service)


class FakeToken(object):
    # FIXME(sirp): let's not use id here
    id = 0

    def __getitem__(self, key):
        return getattr(self, key)

    def __init__(self, **kwargs):
        FakeToken.id += 1
        self.id = FakeToken.id
        for k, v in kwargs.iteritems():
            setattr(self, k, v)


class FakeRequestContext(context.RequestContext):
    def __init__(self, *args, **kwargs):
        kwargs['auth_token'] = kwargs.get('auth_token', 'fake_auth_token')
        return super(FakeRequestContext, self).__init__(*args, **kwargs)


class HTTPRequest(webob.Request):

    @classmethod
    def blank(cls, *args, **kwargs):
        kwargs['base_url'] = 'http://localhost/v2'
        use_admin_context = kwargs.pop('use_admin_context', False)
        out = webob.Request.blank(*args, **kwargs)
        out.environ['engine.context'] = FakeRequestContext('fake_user', 'fake',
                is_admin=use_admin_context)
        return out


class FakeAuthDatabase(object):
    data = {}

    @staticmethod
    def auth_token_get(context, token_hash):
        return FakeAuthDatabase.data.get(token_hash, None)

    @staticmethod
    def auth_token_create(context, token):
        fake_token = FakeToken(created_at=utils.utcnow(), **token)
        FakeAuthDatabase.data[fake_token.token_hash] = fake_token
        FakeAuthDatabase.data['id_%i' % fake_token.id] = fake_token
        return fake_token

    @staticmethod
    def auth_token_destroy(context, token_id):
        token = FakeAuthDatabase.data.get('id_%i' % token_id)
        if token and token.token_hash in FakeAuthDatabase.data:
            del FakeAuthDatabase.data[token.token_hash]
            del FakeAuthDatabase.data['id_%i' % token_id]


class FakeAuthManager(object):
    #NOTE(justinsb): Accessing static variables through instances is FUBAR
    #NOTE(justinsb): This should also be private!
    auth_data = []
    projects = {}

    @classmethod
    def clear_fakes(cls):
        cls.auth_data = []
        cls.projects = {}

    @classmethod
    def reset_fake_data(cls):
        u1 = User('id1', 'guy1', 'acc1', 'secret1', False)
        cls.auth_data = [u1]
        cls.projects = dict(testacct=Project('testacct',
                                             'testacct',
                                             'id1',
                                             'test',
                                              []))

    def add_user(self, user):
        FakeAuthManager.auth_data.append(user)

    def get_users(self):
        return FakeAuthManager.auth_data

    def get_user(self, uid):
        for user in FakeAuthManager.auth_data:
            if user.id == uid:
                return user
        return None

    def get_user_from_access_key(self, key):
        for user in FakeAuthManager.auth_data:
            if user.access == key:
                return user
        return None

    def delete_user(self, uid):
        for user in FakeAuthManager.auth_data:
            if user.id == uid:
                FakeAuthManager.auth_data.remove(user)
        return None

    def create_user(self, name, access=None, secret=None, admin=False):
        u = User(name, name, access, secret, admin)
        FakeAuthManager.auth_data.append(u)
        return u

    def modify_user(self, user_id, access=None, secret=None, admin=None):
        user = self.get_user(user_id)
        if user:
            user.access = access
            user.secret = secret
            if admin is not None:
                user.admin = admin

    def is_admin(self, user_id):
        user = self.get_user(user_id)
        return user.admin

    def is_project_member(self, user_id, project):
        if not isinstance(project, Project):
            try:
                project = self.get_project(project)
            except exc.NotFound:
                raise webob.exc.HTTPUnauthorized()
        return ((user_id in project.member_ids) or
                (user_id == project.project_manager_id))

    def create_project(self, name, manager_user, description=None,
                       member_users=None):
        member_ids = [User.safe_id(m) for m in member_users] \
                     if member_users else []
        p = Project(name, name, User.safe_id(manager_user),
                                 description, member_ids)
        FakeAuthManager.projects[name] = p
        return p

    def delete_project(self, pid):
        if pid in FakeAuthManager.projects:
            del FakeAuthManager.projects[pid]

    def modify_project(self, project, manager_user=None, description=None):
        p = FakeAuthManager.projects.get(project)
        p.project_manager_id = User.safe_id(manager_user)
        p.description = description

    def get_project(self, pid):
        p = FakeAuthManager.projects.get(pid)
        if p:
            return p
        else:
            raise exc.NotFound

    def get_projects(self, user_id=None):
        if not user_id:
            return FakeAuthManager.projects.values()
        else:
            return [p for p in FakeAuthManager.projects.values()
                    if (user_id in p.member_ids) or
                       (user_id == p.project_manager_id)]


class FakeRateLimiter(object):
    def __init__(self, application):
        self.application = application

    @webob.dec.wsgify
    def __call__(self, req):
        return self.application


FAKE_UUID = 'aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa'


def create_fixed_ips(project_id, publics, privates, publics_are_floating):
    if publics is None:
        publics = []
    if privates is None:
        privates = []

    fixed_ips = []
    private_vif = dict(address='aa:bb:cc:dd:ee:ff')
    private_net = dict(label='private', project_id=project_id, cidr_v6=None)

    for private in privates:
        entry = dict(address=private, network=private_net,
                virtual_interface=private_vif, floating_ips=[])
        if publics_are_floating:
            for public in publics:
                entry['floating_ips'].append(dict(address=public))
            # Only add them once
            publics = []
        fixed_ips.append(entry)

    if not publics_are_floating:
        public_vif = dict(address='ff:ee:dd:cc:bb:aa')
        public_net = dict(label='public', project_id=project_id,
                cidr_v6='b33f::/64')
        for public in publics:
            entry = dict(address=public, network=public_net,
                    virtual_interface=public_vif, floating_ips=[])
            fixed_ips.append(entry)
    return fixed_ips


def stub_instance(id, user_id='fake', project_id='fake', host=None,
                  vm_state=None, task_state=None,
                  reservation_id="", uuid=FAKE_UUID, image_ref="10",
                  flavor_id="1", name=None, key_name='',
                  access_ipv4=None, access_ipv6=None, progress=0,
                  auto_disk_config=False, public_ips=None, private_ips=None,
                  public_ips_are_floating=False, display_name=None,
                  include_fake_metadata=True,
                  power_state=None):

    if include_fake_metadata:
        metadata = [models.InstanceMetadata(key='seq', value=id)]
    else:
        metadata = []

    inst_type = instance_types.get_instance_type_by_flavor_id(int(flavor_id))

    if host is not None:
        host = str(host)

    if key_name:
        key_data = 'FAKE'
    else:
        key_data = ''

    fixed_ips = create_fixed_ips(project_id, public_ips, private_ips,
                                 public_ips_are_floating)

    # ReservationID isn't sent back, hack it in there.
    server_name = name or "server%s" % id
    if reservation_id != "":
        server_name = "reservation_%s" % (reservation_id, )

    instance = {
        "id": int(id),
        "created_at": datetime.datetime(2010, 10, 10, 12, 0, 0),
        "updated_at": datetime.datetime(2010, 11, 11, 11, 0, 0),
        "admin_pass": "",
        "user_id": user_id,
        "project_id": project_id,
        "image_ref": image_ref,
        "kernel_id": "",
        "ramdisk_id": "",
        "launch_index": 0,
        "key_name": key_name,
        "key_data": key_data,
        "vm_state": vm_state or vm_states.BUILDING,
        "task_state": task_state,
        "power_state": power_state,
        "memory_mb": 0,
        "vcpus": 0,
        "local_gb": 0,
        "hostname": "",
        "host": host,
        "instance_type": dict(inst_type),
        "user_data": "",
        "reservation_id": reservation_id,
        "mac_address": "",
        "scheduled_at": utils.utcnow(),
        "launched_at": utils.utcnow(),
        "terminated_at": utils.utcnow(),
        "availability_zone": "",
        "display_name": display_name or server_name,
        "display_description": "",
        "locked": False,
        "metadata": metadata,
        "access_ip_v4": access_ipv4,
        "access_ip_v6": access_ipv6,
        "uuid": uuid,
        "progress": progress,
        "auto_disk_config": auto_disk_config,
        "name": "instance-%s" % id,
        "fixed_ips": fixed_ips}

    return instance

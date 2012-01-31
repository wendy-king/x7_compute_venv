
import engineclient.client
import engineclient.v1_1.client
from tests import utils


class ClientTest(utils.TestCase):

    def setUp(self):
        pass

    def test_get_client_class_v2(self):
        output = engineclient.client.get_client_class('2')
        self.assertEqual(output, engineclient.v1_1.client.Client)

    def test_get_client_class_v2_int(self):
        output = engineclient.client.get_client_class(2)
        self.assertEqual(output, engineclient.v1_1.client.Client)

    def test_get_client_class_v1_1(self):
        output = engineclient.client.get_client_class('1.1')
        self.assertEqual(output, engineclient.v1_1.client.Client)

    def test_get_client_class_unknown(self):
        self.assertRaises(engineclient.exceptions.UnsupportedVersion,
                          engineclient.client.get_client_class, '0')

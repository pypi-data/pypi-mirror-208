import unittest
import keyring

from unittest.mock import patch
from keyring.credentials import SimpleCredential
from requests.auth import HTTPBasicAuth

from drb.drivers.odata import ODataServiceNodeCSC
from drb.drivers.odata.odata_utils import ODataUtils
from drb.exceptions.odata import OdataRequestException
from tests.utils import start_mock_odata_csc, stop_mock_odata_csc


class TestAuthenticatedODataNode(unittest.TestCase):
    svc_url = None

    @classmethod
    def setUpClass(cls) -> None:
        cls.svc_url = 'http://auth.domain/csc'
        start_mock_odata_csc(cls.svc_url, auth_required=True)

    @classmethod
    def tearDownClass(cls) -> None:
        stop_mock_odata_csc()

    def test_auth_odata_node(self):
        auth = HTTPBasicAuth('foo', 'bar')
        odata = ODataServiceNodeCSC(self.svc_url, auth=auth)
        self.assertEqual(3, len(odata))

        # FIXME: odata.children[0] represents a Tar data and view as a TarNode
        #        due to the children auto resolution. The received TarBaseNode
        #        not really wrap its base node. So we change expected attribute
        node = odata.children[0]
        self.assertIn(('directory', None), node.attribute_names())
        self.assertEqual(True, node @ 'directory')
        self.assertEqual(True, node.get_attribute('directory'))

        with patch.object(ODataUtils, 'get_type_odata_svc',
                          side_effect=OdataRequestException()):
            with self.assertRaises(OdataRequestException):
                odata = ODataServiceNodeCSC(self.svc_url)
                node = odata.children[0]

    def test_auth_odata_node_with_key_ring(self):
        odata = ODataServiceNodeCSC(self.svc_url)
        with self.assertRaises(Exception):
            len(odata)

        auth = SimpleCredential('foo', 'bar')
        with patch.object(keyring, 'get_credential', return_value=auth):
            odata = ODataServiceNodeCSC(self.svc_url)
            self.assertEqual(3, len(odata))

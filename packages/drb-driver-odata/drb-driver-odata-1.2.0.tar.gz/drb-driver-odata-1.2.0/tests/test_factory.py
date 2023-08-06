import unittest
import keyring
from keyring.credentials import SimpleCredential
from unittest.mock import patch
from drb.drivers.http import DrbHttpNode
from drb.nodes.logical_node import DrbLogicalNode
from drb.drivers.odata import OdataFactory, ODataServiceNodeCSC
from tests.utils import start_mock_odata_csc, stop_mock_odata_csc


class TestOdataFactory(unittest.TestCase):
    svc_url = 'https://Odata_test.com'
    filter = '/Products?filter=Online eq false'

    @classmethod
    def setUpClass(cls) -> None:
        start_mock_odata_csc(cls.svc_url)

    @classmethod
    def tearDownClass(cls) -> None:
        stop_mock_odata_csc()

    def test_create(self):
        factory = OdataFactory()
        node = factory.create(self.svc_url)
        self.assertIsNotNone(node)
        self.assertIsInstance(node, ODataServiceNodeCSC)
        node = factory.create(DrbLogicalNode(self.svc_url))
        self.assertIsNotNone(node)
        self.assertIsInstance(node, ODataServiceNodeCSC)

    def test_create_from_http(self):
        factory = OdataFactory()
        node = factory.create(DrbHttpNode(self.svc_url+self.filter))
        self.assertIsNotNone(node)
        self.assertIsInstance(node, list)
        node = factory.create(DrbHttpNode(self.svc_url+'/Products'))
        self.assertIsNotNone(node)
        self.assertIsInstance(node, list)

    def test_create_with_keyring(self):
        auth = SimpleCredential('foo', 'bar')
        with patch.object(keyring, 'get_credential', return_value=auth):
            factory = OdataFactory()
            node = factory.create(self.svc_url)
            self.assertIsNotNone(node)
            self.assertIsInstance(node, ODataServiceNodeCSC)

import unittest

from drb.exceptions.core import DrbException

from drb.drivers.odata import ODataServiceNodeCSC, ODataProductNode
from tests.utils import start_mock_odata_csc, stop_mock_odata_csc


class TestProductAttributeNode(unittest.TestCase):
    service_url = 'https://gael-systems.com/csc'
    uuid = '0723d9a4-3bbe-305e-b712-5e820058e065'
    node = None

    @classmethod
    def setUpClass(cls) -> None:
        start_mock_odata_csc(cls.service_url)
        cls.node = ODataServiceNodeCSC(cls.service_url)[0]
        cls.node = cls.node.get_impl(ODataProductNode)

    @classmethod
    def tearDownClass(cls) -> None:
        stop_mock_odata_csc()

    def test_name(self):
        self.assertEqual('Attributes', self.node[0].name)

    def test_namespace_uri(self):
        self.assertIsNone(self.node[0].namespace_uri)

    def test_value(self):
        self.assertIsNone(self.node[0].value)

    def test_path(self):
        self.assertEqual(
            f'{self.service_url}/Products({self.uuid})/Attributes',
            self.node[0].path.name)

    def test_parent(self):
        self.assertEqual(self.uuid, self.node[0].parent.get_attribute('Id'))

    def test_attribute(self):
        self.assertEqual({}, self.node[0].attributes)

    def test_children(self):
        self.assertIsNotNone(self.node[0].children)
        self.assertIsInstance(self.node[0].children, list)
        self.assertEqual(49, len(self.node[0].children))

    def test_get_attribute(self):
        with self.assertRaises(DrbException):
            self.node[0].get_attribute('fake')

    def test_has_child(self):
        self.assertTrue(self.node.has_child())

    def test_has_impl(self):
        self.assertFalse(self.node[0].has_impl(int))

    def test_get_impl(self):
        with self.assertRaises(DrbException):
            self.node[0].get_impl(str)

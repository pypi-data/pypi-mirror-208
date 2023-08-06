import json
import os
import unittest

from drb.exceptions.core import DrbException

from drb.drivers.odata import ODataProductNode, ODataServiceNodeCSC
from tests.utils import start_mock_odata_csc, stop_mock_odata_csc


class TestProductNode(unittest.TestCase):
    service_url = 'https://domain.com/csc'
    uuid = '0723d9a4-3bbe-305e-b712-5e820058e065'
    name = 'S2B_OPER_MSI_L0__GR_MPS__20170803T123125_S20170803T090229_' \
           'D12_N02.05.tar'
    node = None

    @classmethod
    def setUpClass(cls) -> None:
        start_mock_odata_csc(cls.service_url)
        cls.node = ODataProductNode(cls.service_url, cls.uuid)

    @classmethod
    def tearDownClass(cls) -> None:
        stop_mock_odata_csc()

    def test_name(self):
        self.assertEqual(self.name, self.node.name)

    def test_namespace_uri(self):
        self.assertIsNone(self.node.namespace_uri)

    def test_value(self):
        self.assertIsNone(self.node.value)

    def test_path(self):
        self.assertEqual(f'{self.service_url}/Products({self.uuid})',
                         self.node.path.name)

    def test_parent(self):
        self.assertIsNone(self.node.parent)
        parent = ODataServiceNodeCSC(self.service_url)
        prd_node = parent[0]
        self.assertEqual(parent, prd_node.parent)

    def test_attributes(self):
        node = self.node.get_impl(ODataProductNode)
        attributes = node.attributes
        path = os.path.join(os.path.dirname(__file__), 'resources',
                            'product1.json')
        with open(path) as f:
            data = json.load(f)

        name = 'Id'
        self.assertEqual(self.uuid, node @ name)
        self.assertEqual(self.uuid, attributes[name, None])
        self.assertEqual(self.uuid, self.node.get_attribute(name))

        name = 'Name'
        self.assertEqual(self.name, attributes[name, None])
        self.assertEqual(self.name, self.node.get_attribute(name))

        name = 'ContentType'
        self.assertEqual(data[name], attributes[name, None])
        self.assertEqual(data[name], self.node.get_attribute(name))

        name = 'ContentLength'
        self.assertEqual(data[name], attributes[name, None])
        self.assertEqual(data[name], self.node.get_attribute(name))

        name = 'OriginDate'
        self.assertEqual(data[name], attributes[name, None])
        self.assertEqual(data[name], self.node.get_attribute(name))

        name = 'PublicationDate'
        self.assertEqual(data[name], attributes[name, None])
        self.assertEqual(data[name], self.node.get_attribute(name))

        name = 'ModificationDate'
        self.assertEqual(data[name], attributes[name, None])
        self.assertEqual(data[name], self.node.get_attribute(name))

        name = 'EvictionDate'
        self.assertEqual(data[name], attributes[name, None])
        self.assertEqual(data[name], self.node.get_attribute(name))

        name = 'Online'
        self.assertTrue(attributes[name, None])
        self.assertTrue(self.node.get_attribute(name))

        name = 'Checksum'
        self.assertEqual(data[name], attributes[name, None])
        self.assertEqual(data[name], self.node.get_attribute(name))

        name = 'ContentDate'
        self.assertEqual(data[name], attributes[name, None])
        self.assertEqual(data[name], self.node.get_attribute(name))

        name = 'Footprint'
        # FIXME: Attributes having null as value are not take in consideration
        self.assertNotIn((name,  None), self.node.attribute_names())
        # self.assertIsNone(attributes[name, None])
        # self.assertIsNone(self.node.get_attribute(name))

        with self.assertRaises(KeyError):
            attributes['@odata.context', None]
        with self.assertRaises(DrbException):
            self.node.get_attribute('@odata.context')

    def test_children(self):
        children = self.node.get_impl(ODataProductNode).children
        self.assertIsNotNone(children)
        self.assertTrue(self.node.has_child("Attributes"))
        self.assertFalse(self.node.has_child("Attributes", 'ns'))
        self.assertIsInstance(children, list)
        self.assertEqual(1, len(children))
        self.assertEqual('Attributes', children[0].name)

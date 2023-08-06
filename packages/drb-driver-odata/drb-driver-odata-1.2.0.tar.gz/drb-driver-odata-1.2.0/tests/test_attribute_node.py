import unittest

from drb.exceptions.core import DrbException

from drb.drivers.odata import ODataServiceNodeCSC, ODataProductNode
from tests.utils import start_mock_odata_csc, stop_mock_odata_csc


class TestAttributeNode(unittest.TestCase):
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
        self.assertEqual('lineage', self.node[0][0].name)
        self.assertEqual('instrumentShortName', self.node[0][2].name)

    def test_namespace_uri(self):
        for i in range(49):
            self.assertIsNone(self.node[0][i].namespace_uri)

    def test_value(self):
        self.assertEqual('MSI', self.node[0][2].value)
        self.assertEqual(-13.5554284611837, self.node[0][16].value)
        self.assertEqual(23371, self.node[0][33].value)

    def test_path(self):
        self.assertEqual(f'{self.node.path.name}/Attributes/lineage',
                         self.node[0][0].path.name)
        self.assertEqual(f'{self.node.path.name}'
                         f'/Attributes/instrumentShortName',
                         self.node[0][2].path.name)

    def test_parent(self):
        for i in range(49):
            self.assertEqual(self.node[0], self.node[0][i].parent)

    def test_attributes(self):
        attributes = self.node[0][25].attributes
        self.assertEqual('endingDateTime', attributes['Name', None])
        with self.assertRaises(KeyError):
            attributes['test_name', 'test_ns']

    def test_children(self):
        for i in range(49):
            self.assertEqual([], self.node[0][i].children)

    def test_get_attribute(self):
        self.assertEqual('endingDateTime',
                         self.node[0][25].get_attribute('Name'))
        self.assertEqual('DateTimeOffset',
                         self.node[0][25].get_attribute('ValueType'))
        self.assertEqual('2019-12-13T10:51:40Z',
                         self.node[0][25].get_attribute('Value'))
        with self.assertRaises(DrbException):
            self.node[0].get_attribute('test')

    def test_has_child(self):
        for i in range(49):
            self.assertFalse(self.node[0][i].has_child())

    def test_has_impl(self):
        for i in range(49):
            self.assertFalse(self.node[0][i].has_impl(int))

    def test_get_impl(self):
        for i in range(49):
            with self.assertRaises(DrbException):
                self.node[0][i].get_impl(str)

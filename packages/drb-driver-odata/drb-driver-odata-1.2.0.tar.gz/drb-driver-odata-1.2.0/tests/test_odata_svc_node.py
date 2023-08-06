import io
import unittest
import uuid
import re

import drb.drivers.tar
from drb.exceptions.core import DrbException

from drb.drivers.odata import ODataServiceNodeCSC, \
    ODataServiceType, ODataProductNode, ODataServiceNodeList, \
    ODataQueryPredicate
from tests.utils import start_mock_odata_csc, stop_mock_odata_csc


class TestODataServiceNode(unittest.TestCase):
    svc_url = 'https://gael-systems.com/odata/csc'
    node = None

    @classmethod
    def setUpClass(cls) -> None:
        start_mock_odata_csc(cls.svc_url)
        cls.node = ODataServiceNodeCSC(cls.svc_url)

    @classmethod
    def tearDownClass(cls) -> None:
        stop_mock_odata_csc()

    def test_type_service(self):
        self.assertEqual(ODataServiceType(1), self.node.type_service)
        self.node._type = None
        self.assertEqual(ODataServiceType(1), self.node.type_service)

    def test_name(self):
        self.assertEqual(self.svc_url, self.node.name)

    def test_namespace_uri(self):
        self.assertEqual('OData.CSC', self.node.namespace_uri)

    def test_value(self):
        self.assertIsNone(self.node.value)

    def test_path(self):
        self.assertEqual(self.svc_url, self.node.path.name)

    def test_parent(self):
        self.assertIsNone(self.node.parent)

    def test_attributes(self):
        self.assertEqual({}, self.node.attributes)

    def test_children(self):
        expected = [
            ODataProductNode(
                self.svc_url, '0723d9a4-3bbe-305e-b712-5e820058e065'),
            ODataProductNode(
                self.svc_url, '0723d9bf-02a2-3e99-b1b3-f6d81de84b62'),
            ODataProductNode(
                self.svc_url, '0723ddbc-b0e7-4702-abeb-de257b9f4094'),
        ]
        children = self.node.children
        self.assertIsNotNone(children)
        self.assertIsInstance(children, list)
        self.assertEqual(expected[1], children[1].get_impl(ODataProductNode))
        self.assertEqual(expected[-1], children[-2].get_impl(ODataProductNode))

        self.assertIsInstance(children[:2], ODataServiceNodeList)

        itr = iter(children)
        self.assertEqual(expected[0], next(itr).get_impl(ODataProductNode))
        self.assertEqual(expected[1], next(itr).get_impl(ODataProductNode))
        self.assertEqual(expected[2], next(itr).get_impl(ODataProductNode))

    def test_len(self):
        self.assertEqual(3, len(self.node))

    def test_get_attribute(self):
        with self.assertRaises(DrbException):
            att = self.node.get_attribute('foo')

    def test_has_impl(self):
        self.assertFalse(self.node.has_impl(io.BytesIO))

    def test_has_child(self):
        self.assertFalse(self.node.has_child('Banana'))
        self.assertTrue(self.node.has_child(
            'S2B_OPER_MSI_L0__GR_EPAE_20180703T214414_S201807'
            '03T165907_D05_N02.06.tar'
        ))
        self.assertFalse(self.node.has_child(
            'S2B_OPER_MSI_L0__GR_EPAE_20180703T214414_S2'
            '0180703T165907_D05_N02.06.tar',
            'Test'))

    def test_hash(self):
        self.assertEqual(hash(self.svc_url),
                         self.node.__hash__())

    def test_bracket_browse(self):
        prd2 = {
            'uuid': '0723d9bf-02a2-3e99-b1b3-f6d81de84b62',
            'name': 'S2B_OPER_MSI_L0__GR_EPAE_20180703T214414_S20180703T165907'
                    '_D05_N02.06.tar',
        }

        # FIXME: odata.children[0] represents a Tar data and view as a TarNode
        #        due to the children auto resolution. The received TarBaseNode
        #        not really wrap its base node. So we change expected attribute
        self.assertIsInstance(self.node[1], drb.drivers.tar.DrbBaseTarNode)
        self.assertEqual(self.node[1].name, prd2['name'])
        self.assertIsInstance(self.node[-3], drb.drivers.tar.DrbBaseTarNode)
        self.assertEqual(self.node[-3].name, prd2['name'])
        with self.assertRaises(IndexError):
            n = self.node[42]

        # tuple(str, str, int) -> by Name
        actual_node = self.node[prd2['name'], None, 0]
        self.assertEqual(actual_node.name, prd2['name'])
        actual_node = self.node[prd2['name'], 0]
        self.assertEqual(actual_node.name, prd2['name'])
        actual_node = self.node[prd2['name']]
        self.assertEqual(actual_node.name, prd2['name'])

        n = self.node[ODataQueryPredicate(filter=f"Name eq '{prd2['name']}'")]
        self.assertIsInstance(n, list)
        self.assertEqual(1, len(n))
        self.assertEqual(prd2['name'], n[0].name)

        with self.assertRaises(KeyError):
            n = self.node['test']
        with self.assertRaises(KeyError):
            n = self.node['test', 1]
        with self.assertRaises(KeyError):
            n = self.node[prd2['name'], 'ns']
        with self.assertRaises(KeyError):
            n = self.node[prd2['name'], 'ns', 1]

        # UUID -> by Id
        self.assertEqual(prd2['name'], self.node[uuid.UUID(prd2['uuid'])].name)
        with self.assertRaises(KeyError):
            fake_uuid = prd2['uuid'][:-2] + 'f'
            n = self.node[fake_uuid]

        with self.assertRaises(TypeError):
            n = self.node[b"helloWorld"]

    def test_equals(self):
        self.assertEqual(self.node, ODataServiceNodeCSC(self.svc_url))

    def test_prepare_filter(self):
        pat = r"\d{4}-\d{2}-\d{2}\w{3}\W\w{2}\W\w{3}"

        self.assertTrue(re.search(pat,
                                  self.node.prepare_filter(None)))
        self.assertIn('PublicationDate', self.node.prepare_filter(None))
        self.assertEqual('PublicationDate',
                         self.node.prepare_filter('PublicationDate'))
        self.assertIn('foo', self.node.prepare_filter('foo'))

import unittest
import unittest.mock as mocking
import uuid

from drb.drivers.odata import ODataServiceNodeDias, \
    ODataServiceType, ODataProductNode, ODataServiceNodeList
from drb.drivers.odata.odata_utils import ODataUtils, ODataQueryPredicate
from tests.utils import start_mock_odata_dias, \
    stop_mock_odata_csc, dias_products


class TestODataDiasServiceNode(unittest.TestCase):
    svc_url = 'https://gael-systems.com/odata/dias'
    node = None

    @classmethod
    def setUpClass(cls) -> None:
        start_mock_odata_dias(cls.svc_url)
        cls.node = ODataServiceNodeDias(cls.svc_url)
        cls.node._type = ODataServiceType.ONDA_DIAS

    @classmethod
    def tearDownClass(cls) -> None:
        stop_mock_odata_csc()
        cls.node._type = ODataServiceType.CSC

    def test_name(self):
        self.assertEqual(self.svc_url, self.node.name)

    def test_namespace_uri(self):
        self.assertEqual('Ens', self.node.namespace_uri)

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
                self.svc_url, 'da4cdfee-9fef-4ab1-b4a2-20f9ec8005bd'),
            ODataProductNode(
                self.svc_url, '34416861-c364-44be-8bc9-16829f32cf31'),
            ODataProductNode(
                self.svc_url, 'c3f89d3d-3a06-4e42-9903-a5d07ab5c642')
        ]
        with mocking.patch.object(ODataUtils, 'req_svc_products',
                                  return_value=(dias_products, -1)):
            children = self.node.children
            self.assertIsNotNone(children)
            self.assertIsInstance(children, list)
            self.assertEqual(expected[1],
                             children[1].get_impl(ODataProductNode))
            self.assertEqual(expected[-1],
                             children[-1].get_impl(ODataProductNode))
            self.assertIsInstance(children[:2], ODataServiceNodeList)
            self.assertIsInstance(children[1:-1], ODataServiceNodeList)

        with mocking.patch.object(ODataUtils, 'req_svc_products',
                                  return_value=dias_products):
            itr = iter(children)
            self.assertEqual(expected[0], next(itr).get_impl(ODataProductNode))
            self.assertEqual(expected[1], next(itr).get_impl(ODataProductNode))
            self.assertEqual(expected[2], next(itr).get_impl(ODataProductNode))

    def test_len(self):
        self.assertEqual(3, len(self.node))

    def test_bracket_browse(self):
        prd2 = {
            'uuid': '34416861-c364-44be-8bc9-16829f32cf31',
            'name': 'S2B_MSIL2A_20180328T120349_N0207_R066_'
                    'T29VLD_20180328T175102.zip'
        }

        # int
        with mocking.patch.object(ODataUtils, 'req_svc_products',
                                  return_value=(dias_products, -1)):
            node = self.node[1]
            self.assertEqual(prd2['uuid'], node.get_attribute('id'))
            node = self.node[-2].get_impl(ODataProductNode)
            self.assertEqual(prd2['uuid'], node.get_attribute('id'))
            with self.assertRaises(IndexError):
                n = self.node[42]

        # # tuple(str, str, int) -> by Name
        actual_node = self.node[prd2['name']].get_impl(ODataProductNode)
        self.assertEqual(prd2['uuid'], actual_node.get_attribute('id'))
        self.assertEqual(prd2['uuid'], actual_node @ 'id')

        n = self.node[ODataQueryPredicate(filter=f"Name eq '{prd2['name']}'")]
        self.assertIsInstance(n, list)
        self.assertEqual(3, len(n))

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
        self.assertEqual(self.node, ODataServiceNodeDias(self.svc_url))

    def test_prepare_filter(self):

        result = '%22creationDate:[1900-05-10T00:00:00.000Z TO NOW]%22'
        self.assertEqual(result, self.node.prepare_filter(None))

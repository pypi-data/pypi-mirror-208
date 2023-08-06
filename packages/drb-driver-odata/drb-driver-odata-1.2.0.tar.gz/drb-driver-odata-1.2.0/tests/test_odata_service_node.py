import uuid
import unittest

from drb.drivers.odata import ODataServiceNodeCSC, \
    ODataProductNode, ODataQueryPredicate
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

    def test_index(self):
        child = self.node[0]
        self.assertIsNotNone(child)
        self.assertNotIsInstance(child, ODataProductNode)

    def test_slice(self):
        children = self.node[0:3]
        child = children[0]
        self.assertIsNotNone(children)
        self.assertIsInstance(children, list)
        self.assertIsNotNone(child)
        self.assertNotIsInstance(child, ODataProductNode)

    def test_uuid(self):
        prd_uuid = '0723d9bf-02a2-3e99-b1b3-f6d81de84b62'
        child = self.node[uuid.UUID(prd_uuid)]
        self.assertIsNotNone(child)
        self.assertNotIsInstance(child, ODataProductNode)

    def test_name(self):
        prd_name = "S2B_OPER_MSI_L0__GR_EPAE_20180703T214414_" \
                   "S20180703T165907_D05_N02.06.tar"
        child = self.node[prd_name]
        self.assertIsNotNone(child)
        self.assertNotIsInstance(child, ODataProductNode)

    def test_resolve(self):
        prd_name = "banana.png"
        child = self.node[prd_name]
        self.assertIsNotNone(child)
        self.assertIsInstance(child, ODataProductNode)

    def test_filter_predicate(self):
        prd_name = "S2B_OPER_MSI_L0__GR_EPAE_20180703T214414_" \
                   "S20180703T165907_D05_N02.06.tar"
        children = self.node[ODataQueryPredicate(
            filter=f"Name eq '{prd_name}'")]
        child = children[0]
        self.assertIsNotNone(child)
        self.assertNotIsInstance(child, ODataProductNode)

    def test_slice_children(self):
        children = self.node.children[0:3]
        self.assertIsNotNone(children)
        self.assertIsInstance(children, list)
        for i in range(2):
            child = children[i]
            self.assertIsNotNone(child)
            self.assertNotIsInstance(child, ODataProductNode)

        with self.assertRaises(IndexError):
            child = children[8]

        with self.assertRaises(KeyError):
            child = children['foo']

    def test_iter_children(self):
        children = self.node.children[0:3]
        itr = iter(children)
        for child in itr:
            self.assertIsNotNone(child)
            self.assertNotIsInstance(child, ODataProductNode)

    def test_append(self):
        children = self.node.children[0:3]
        with self.assertRaises(NotImplementedError):
            child = children.append('foo')

    def test_clear(self):
        children = self.node.children[0:3]
        with self.assertRaises(NotImplementedError):
            children.clear()

    def test_copy(self):
        children = self.node.children[0:3]
        with self.assertRaises(NotImplementedError):
            children.copy()

    def test_count(self) -> int:
        children = self.node.children[0:3]
        with self.assertRaises(NotImplementedError):
            children.count(10)

    def test_extend(self):
        children = self.node.children[0:3]
        with self.assertRaises(NotImplementedError):
            children.extend([])

    def test_insert(self):
        children = self.node.children[0:3]
        with self.assertRaises(NotImplementedError):
            children.insert(2, 'foo')

    def test_pop(self):
        children = self.node.children[0:3]
        with self.assertRaises(NotImplementedError):
            children.pop(2)

    def test_remove(self):
        children = self.node.children[0:3]
        with self.assertRaises(NotImplementedError):
            children.remove(10)

    def test_reverse(self):
        children = self.node.children[0:3]
        with self.assertRaises(NotImplementedError):
            children.reverse()

    def test_sort(self):
        children = self.node.children[0:3]
        with self.assertRaises(NotImplementedError):
            children.sort()

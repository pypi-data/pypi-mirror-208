import io
import unittest
import uuid

import unittest.mock as mocking

from drb.drivers.http.http import DrbHttpResponse
from drb.exceptions.core import DrbException, DrbNotImplementationException
from requests import Response

from drb.drivers.odata import ODataServiceNodeCSC, \
    ODataOrderNode, ODataProductNode
from drb.drivers.odata.odata_utils import ODataUtils
from tests.utils import start_mock_odata_csc, stop_mock_odata_csc


class TestODataOrders(unittest.TestCase):
    svc_url = 'https://gael-systems.com/odata/csc'
    orders = None
    service = None

    @classmethod
    def setUpClass(cls) -> None:
        start_mock_odata_csc(cls.svc_url)
        cls.service = ODataServiceNodeCSC(cls.svc_url)
        cls.orders = cls.service.orders

    @classmethod
    def tearDownClass(cls) -> None:
        stop_mock_odata_csc()

    def test_len_init(self):
        self.assertEqual(3, len(ODataServiceNodeCSC(self.svc_url).orders))

    def test_order_list(self):
        self.assertEqual(3, len(self.orders))
        self.assertEqual(
            self.orders[1:][0].name,
            self.orders[1].name)
        self.assertEqual(2, len(self.orders[0:2]))
        order_uuid = '56ac8297-e55e-4682-87c8-059e1e02260c'
        self.assertEqual(order_uuid, self.orders[uuid.UUID(order_uuid)].name)
        with self.assertRaises(KeyError):
            self.orders['Banana']

    def test_order_node(self):
        self.assertIsInstance(self.orders[0], ODataOrderNode)
        self.assertEqual('56ac8297-e55e-4682-87c8-059e1e02260c',
                         self.orders[0].name)
        self.assertIsInstance(self.orders[0].parent, ODataServiceNodeCSC)
        self.assertEqual('https://gael-systems.com/odata/csc',
                         self.orders[0].parent.name)
        self.assertEqual('https://gael-systems.com/odata/csc/'
                         'Orders(56ac8297-e55e-4682-87c8-059e1e02260c)',
                         self.orders[0].path.original_path)
        self.assertEqual([], self.orders[0].children)
        self.assertIsNone(self.orders[0].namespace_uri)
        self.assertIsNone(self.orders[0].value)
        self.assertFalse(self.orders[0].has_impl(io.BytesIO))
        self.assertFalse(self.orders[0].has_impl(str))
        with self.assertRaises(DrbNotImplementationException):
            self.assertIsNone(self.orders[0].get_impl(io.BytesIO))
        with self.assertRaises(DrbNotImplementationException):
            self.assertIsNone(self.orders[0].get_impl(str))

    def test_order_product(self):
        self.assertIsInstance(self.orders[0].product, ODataProductNode)
        self.assertEqual("S2B_OPER_MSI_L0__GR_MPS__20170803T123125"
                         "_S20170803T090229_D12_N02.05.tar",
                         self.orders[0].product.name)

    def test_order_attributes(self):
        self.assertIsInstance(self.orders[0].attributes, dict)
        # Attribute having None as value are not saved
        self.assertEqual(5, len(self.orders[0].attributes))
        self.assertEqual("in_progress", self.orders[0].get_attribute('Status'))

        with self.assertRaises(DrbException):
            self.orders[0].get_attribute('Banana')

        with self.assertRaises(DrbException):
            self.orders[0].get_attribute('Banana', 'Fruit')

    def test_order_cancel(self):
        with mocking.patch.object(ODataUtils, 'cancel_order',
                                  return_value=DrbHttpResponse(
                                      self.svc_url,
                                      Response())
                                  ):
            self.assertIsInstance(self.orders[0].cancel(), DrbHttpResponse)

    def test_order_by_uuid(self):
        self.assertIsInstance(
            self.orders[uuid.UUID('56ac8297-e55e-4682-87c8-059e1e02260c')],
            ODataOrderNode
        )

    def test_order_status(self):
        self.assertEqual(
            'in_progress',
            self.orders[uuid.UUID(
                '56ac8297-e55e-4682-87c8-059e1e02260c')].status
        )

    def test_order_eta(self):
        self.assertEqual(
            '2023-02-17T09:47:58.676Z',
            self.orders[uuid.UUID(
                '56ac8297-e55e-4682-87c8-059e1e02260c')].order_eta
        )

    def test_send_order(self):
        prd = self.service[uuid.UUID('0723ddbc-b0e7-4702-abeb-de257b9f4094')]
        self.assertIsInstance(prd.order(), ODataOrderNode)

        with mocking.patch.object(ODataProductNode, 'get_attribute',
                                  return_value=True
                                  ):
            with self.assertRaises(TypeError):
                prd.order()

        prd2 = self.service[uuid.UUID('0723d9a4-3bbe-305e-b712-5e820058e065')]
        with self.assertRaises(AttributeError):
            prd2.order()

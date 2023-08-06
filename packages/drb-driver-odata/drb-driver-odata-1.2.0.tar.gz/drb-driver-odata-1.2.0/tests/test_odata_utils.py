import io
import json
import os
import uuid
import unittest

from unittest.mock import patch

from drb.drivers.http import DrbHttpNode
from drb.nodes.logical_node import DrbLogicalNode

from drb.drivers.odata.odata_utils import ODataUtils, \
    ODataServiceType, ODataQueryPredicate
from drb.exceptions.odata import OdataRequestException


class TestODataUtils(unittest.TestCase):
    resource_dir = None

    @classmethod
    def setUpClass(cls) -> None:
        cls.resource_dir = os.path.join(os.path.dirname(__file__), 'resources')

    def test_get_type_odata_svc(self):
        svc_url = 'https://foobar.com/odata/v4'

        svc_metadata_path = os.path.join(self.resource_dir, 'csc_metadata.xml')
        with open(svc_metadata_path, 'rb') as resp:
            with patch.object(DrbHttpNode, 'get_impl', return_value=resp):
                t = ODataUtils.get_type_odata_svc(svc_url)
            self.assertEqual(ODataServiceType.CSC, t)

        svc_metadata_path = os.path.join(self.resource_dir,
                                         'dhus_metadata.xml')
        with open(svc_metadata_path, 'rb') as resp:
            with patch.object(DrbHttpNode, 'get_impl', return_value=resp):
                t = ODataUtils.get_type_odata_svc(svc_url)
            self.assertEqual(ODataServiceType.DHUS, t)

        svc_metadata_path = os.path.join(self.resource_dir,
                                         'dias_metadata.xml')
        with open(svc_metadata_path, 'rb') as resp:
            with patch.object(DrbHttpNode, 'get_impl', return_value=resp):
                t = ODataUtils.get_type_odata_svc(svc_url)
            self.assertEqual(ODataServiceType.ONDA_DIAS, t)

        svc_metadata_path = os.path.join(self.resource_dir,
                                         'no_csc_metadata.xml')
        with open(svc_metadata_path, 'rb') as resp:
            with patch.object(DrbHttpNode, 'get_impl', return_value=resp):
                t = ODataUtils.get_type_odata_svc(svc_url)
            self.assertEqual(ODataServiceType.UNKNOWN, t)

        with io.BytesIO(b'something else') as resp:
            with patch.object(DrbHttpNode, 'get_impl', return_value=resp):
                t = ODataUtils.get_type_odata_svc(svc_url)
            self.assertEqual(ODataServiceType.UNKNOWN, t)

    def test_http_node_to_json(self):
        url = 'https://my.domain.com'

        json_data = os.path.join(self.resource_dir, 'product1.json')
        with open(json_data, 'rb') as resp:
            with patch.object(DrbHttpNode, 'get_impl', return_value=resp):
                data = ODataUtils.http_node_to_json(DrbHttpNode(url))
        self.assertEqual(18388992, data['ContentLength'])
        self.assertEqual('0723d9a4-3bbe-305e-b712-5e820058e065', data['Id'])
        self.assertEqual(14, len(data))

        with io.BytesIO(b'<some><xml>content</xml><some>') as resp:
            with patch.object(DrbHttpNode, 'get_impl', return_value=resp):
                with self.assertRaises(OdataRequestException):
                    ODataUtils.http_node_to_json(DrbHttpNode(url))

        with self.assertRaises(OdataRequestException):
            ODataUtils.http_node_to_json(DrbLogicalNode('node'))

    def test_req_svc(self):
        expected = {
            "@odata.context": "$metadata",
            "value": [
                {"name": "Orders", "url": "Orders"},
                {"name": "Products", "url": "Products"}
            ]
        }
        with io.BytesIO(json.dumps(expected).encode()) as resp:
            with patch('drb.drivers.odata.odata_node.OdataNode') as odata:
                odata.get_service_url.return_value = 'https://test.com'
                odata.get_auth.return_value = None
                with patch.object(DrbHttpNode, 'get_impl', return_value=resp):
                    actual = ODataUtils.req_svc(odata)
        self.assertEqual(expected, actual)

    def test_req_svc_count(self):
        expected = 42
        with patch('drb.drivers.odata.odata_node.OdataNode') as odata:
            odata.get_service_url.return_value = 'https://test.com'
            odata.get_auth.return_value = None
            with io.BytesIO(str(expected).encode()) as resp:
                with patch.object(DrbHttpNode, 'get_impl', return_value=resp):
                    actual = ODataUtils.req_svc_count(odata)
        self.assertEqual(expected, actual)

    @patch('drb.drivers.odata.odata_node.OdataNode')
    def test_req_svc_products(self, odata):
        data = {
            '@odata.count': 132,
            'value': [
                {
                    'Id': str(uuid.uuid4()),
                    'Name': 'name#1',
                },
                {
                    'Id': str(uuid.uuid4()),
                    'Name': 'name#2',
                },
            ],
        }
        odata.get_service_url.return_value = 'https://my.domain.com/odata'
        odata.get_auth.return_value = None

        with io.BytesIO(json.dumps(data).encode()) as resp:
            with patch.object(DrbHttpNode, 'get_impl', return_value=resp):
                actual = ODataUtils.req_svc_products(odata,
                                                     filter='criteria#filter',
                                                     skip=1, top=2, order='Id')
        self.assertEqual(data['value'][0], actual[0])

        with io.BytesIO(json.dumps(data).encode()) as resp:
            with patch.object(DrbHttpNode, 'get_impl', return_value=resp):
                actual = ODataUtils.req_svc_products(odata, count=True)
        self.assertEqual((data['value'], data['@odata.count']), actual)

    @patch('drb.drivers.odata.odata_node.OdataNode')
    def test_req_product_by_uuid(self, odata):
        expected = {
            'Id': str(uuid.uuid4()),
            'Name': 'foobar',
        }

        with io.BytesIO(json.dumps(expected).encode()) as resp:
            with patch.object(DrbHttpNode, 'get_impl', return_value=resp):
                actual = ODataUtils.req_product_by_uuid(odata, expected['Id'])

        self.assertEqual(expected, actual)

    @patch('drb.drivers.odata.odata_node.OdataNode')
    def test_req_product_download(self, odata):
        prd_id = str(uuid.uuid4())
        expected = b'downloading_data'

        odata.get_service_url.return_value = 'https://my.domain.com'
        odata.get_auth.return_value = None
        type(odata).type_service = unittest.mock.PropertyMock(
            return_value=ODataServiceType.CSC)

        with io.BytesIO(expected) as resp:
            with patch.object(DrbHttpNode, 'get_impl', return_value=resp):
                actual = ODataUtils.req_product_download(odata, prd_id)
            self.assertEqual(expected, actual.read())


class TestODataQueryPredicate(unittest.TestCase):
    def test_matches(self):
        self.assertFalse(ODataQueryPredicate().matches(DrbLogicalNode('foo')))

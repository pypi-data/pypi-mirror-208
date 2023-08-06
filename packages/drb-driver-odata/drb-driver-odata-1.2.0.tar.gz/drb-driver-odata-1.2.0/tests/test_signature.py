import unittest
import uuid

from drb.core.factory import FactoryLoader
from drb.topics.topic import TopicCategory
from drb.topics.dao import ManagerDao
from drb.nodes.logical_node import DrbLogicalNode
from drb.drivers.odata import OdataFactory
from tests.utils import start_mock_odata_csc, stop_mock_odata_csc


class TestOdataSignature(unittest.TestCase):
    svc_url = 'http+odata://my.domain.com/csc'
    svc_url_false = 'https://my.domain.com/csc'
    fc_loader = None
    ic_loader = None
    odata_id = uuid.UUID('a32c5d56-409e-11ec-973a-0242ac130003')

    @classmethod
    def setUpClass(cls) -> None:
        start_mock_odata_csc(cls.svc_url)
        cls.fc_loader = FactoryLoader()
        cls.ic_loader = ManagerDao()

    @classmethod
    def tearDownClass(cls) -> None:
        stop_mock_odata_csc()

    def test_impl_loading(self):
        factory_name = 'odata'

        factory = self.fc_loader.get_factory(factory_name)
        self.assertIsNotNone(factory)
        self.assertIsInstance(factory, OdataFactory)

        topic = self.ic_loader.get_drb_topic(self.odata_id)
        self.assertIsNotNone(factory)
        self.assertEqual(self.odata_id, topic.id)
        self.assertEqual('OData Copernicus Space Component', topic.label)
        self.assertIsNone(topic.description)
        self.assertEqual(TopicCategory.PROTOCOL, topic.category)
        self.assertEqual('odata', topic.factory)

    def test_impl_signatures(self):
        topic = self.ic_loader.get_drb_topic(self.odata_id)
        node = DrbLogicalNode(self.svc_url)
        self.assertTrue(topic.matches(node))

        node = DrbLogicalNode(f'{self.svc_url_false}')
        self.assertFalse(topic.matches(node))

        node = DrbLogicalNode(f'http://not.odata.svc')
        self.assertFalse(topic.matches(node))

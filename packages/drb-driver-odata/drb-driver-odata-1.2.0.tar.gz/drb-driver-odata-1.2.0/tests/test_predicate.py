import os
import unittest
import httpretty

from drb.drivers.odata import (
    ODataServiceNodeCSC, ODataQueryPredicate,
    ExpressionFunc, ExpressionType)


def odata_metadata_query(request, uri, headers):
    stub = '<odata><foo><bar Namespace="OData.CSC"></bar></foo></odata>'
    return 200, headers, stub


class TestODataPredicate(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        os.path.join(os.path.dirname(__file__), 'resources')
        httpretty.enable()

    @classmethod
    def tearDownClass(cls) -> None:
        httpretty.disable()
        httpretty.reset()

    def test_custom_query(self):
        url = 'http://gael-systems.com/odata'
        my_filter = "startswith(Name,'S2')"
        my_order = "ContentLength desc"
        products_url = f'{url}/Products'

        def callback_checker(request, uri, headers):
            self.assertIn('$filter', request.querystring.keys())
            self.assertIn(my_filter, request.querystring['$filter'][0])
            self.assertIn('$orderby', request.querystring.keys())
            self.assertIn(request.querystring['$orderby'][0],
                          [
                              my_order,
                              f"{my_order} PublicationDate asc"
                          ])
            self.assertIn('$format', request.querystring.keys())
            self.assertEqual('json', request.querystring['$format'][0])
            if '$count' in request.querystring \
                    and request.querystring['$count'][0]:
                return 200, headers, '{"@odata.count": 0,"value": []}'
            return 200, headers, '{"value": []}'

        httpretty.register_uri(httpretty.GET, f'{url}/$metadata',
                               odata_metadata_query)
        httpretty.register_uri(httpretty.GET, products_url, callback_checker)

        node = ODataServiceNodeCSC(url)
        children = node[
            ODataQueryPredicate(filter=my_filter, order=my_order)]

        self.assertIsNotNone(children)
        self.assertIsInstance(children, list)
        self.assertEqual(0, len(children))

        children = node[
            ODataQueryPredicate(
                filter=ExpressionFunc.startswith(
                                    ExpressionType.property('Name'),
                                    'S2'
                                ),
                order=(
                    ExpressionType.property('ContentLength'),
                    ExpressionType.property('desc')
                )
            )]

        self.assertIsNotNone(children)
        self.assertIsInstance(children, list)
        self.assertEqual(0, len(children))

        children = node[
            ODataQueryPredicate(
                filter=ExpressionFunc.startswith(
                                    ExpressionType.property('Name'),
                                    'S2'
                                ).evaluate(),
                order=[
                    (
                        ExpressionType.property('ContentLength'),
                        ExpressionType.property('desc')
                    ),
                    (
                        ExpressionType.property('PublicationDate'),
                        ExpressionType.property('asc')
                    )
                    ]
            )]

        self.assertIsNotNone(children)
        self.assertIsInstance(children, list)
        self.assertEqual(0, len(children))

        children = node[ODataQueryPredicate(filter=my_filter, order=my_order)]
        self.assertIsNotNone(children)
        self.assertIsInstance(children, list)
        self.assertEqual(0, len(children))

    def test_custom_query_with_count(self):
        url = 'http://gael-systems.com/odata2'
        my_filter = "startswith(Name,'S2')"
        my_order = "ContentLength desc"
        products_url = f'{url}/Products'

        def callback_checker(request, uri, headers):
            self.assertIn('$filter', request.querystring.keys())
            self.assertIn(my_filter, request.querystring['$filter'][0])
            self.assertIn('$orderby', request.querystring.keys())
            self.assertIn(my_order, request.querystring['$orderby'][0])
            self.assertIn('$format', request.querystring.keys())
            self.assertEqual('json', request.querystring['$format'][0])
            self.assertIn('$count', request.querystring.keys())
            self.assertTrue('true', request.querystring['$count'][0])
            return 200, headers, '{"@odata.count": 100, "value": []}'

        httpretty.register_uri(httpretty.GET, f'{url}/$metadata',
                               odata_metadata_query)
        httpretty.register_uri(httpretty.GET, products_url, callback_checker)

        node = ODataServiceNodeCSC(url)
        children = node[ODataQueryPredicate(filter=my_filter, order=my_order)]

        self.assertIsNotNone(children)
        self.assertIsInstance(children, list)
        self.assertEqual(100, len(children))

        children = node[ODataQueryPredicate(filter=my_filter, order=my_order)]
        self.assertIsNotNone(children)
        self.assertIsInstance(children, list)
        self.assertEqual(100, len(children))

    def test_custom_query_without_count(self):
        url = 'http://gael-systems.com/odata'
        my_filter = "startswith(Name,'S2')"
        my_order = "ContentLength desc"
        products_url = f'{url}/Products'

        def callback_checker(request, uri, headers):
            self.assertIn('$filter', request.querystring.keys())
            self.assertIn(my_filter, request.querystring['$filter'][0])
            self.assertIn('$orderby', request.querystring.keys())
            self.assertEqual(my_order, request.querystring['$orderby'][0])
            self.assertIn('$format', request.querystring.keys())
            self.assertEqual('json', request.querystring['$format'][0])
            self.assertIn('$count', request.querystring.keys())
            return 200, headers, '{"value": [], "@odata.count": 0}'

        httpretty.register_uri(httpretty.GET, f'{url}/$metadata',
                               odata_metadata_query)
        httpretty.register_uri(httpretty.GET, products_url, callback_checker)

        node = ODataServiceNodeCSC(url)
        children = node[ODataQueryPredicate(filter=my_filter, order=my_order)]

        self.assertIsNotNone(children)
        self.assertIsInstance(children, list)
        self.assertEqual(0, len(children))

        children = node[ODataQueryPredicate(filter=my_filter, order=my_order)]
        self.assertIsNotNone(children)
        self.assertIsInstance(children, list)
        self.assertEqual(0, len(children))

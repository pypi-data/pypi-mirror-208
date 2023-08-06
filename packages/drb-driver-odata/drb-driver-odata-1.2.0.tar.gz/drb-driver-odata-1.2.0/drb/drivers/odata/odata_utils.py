import json
import io
from enum import Enum

from drb.core import Predicate
from drb.drivers.http import DrbHttpNode
from drb.exceptions.core import DrbException
from requests.auth import AuthBase
from typing import List
from defusedxml import ElementTree
from defusedxml.ElementTree import ParseError

from .expression import Expression
from .odata_node import OdataNode
from ...exceptions.odata import OdataRequestException


class ODataServiceType(Enum):
    UNKNOWN = 0
    CSC = 1
    DHUS = 2
    ONDA_DIAS = 3


class ODataUtils:

    @staticmethod
    def http_node_to_json(node: DrbHttpNode) -> dict:
        try:
            with node.get_impl(io.BytesIO) as stream:
                data = json.load(stream)
                if 'error' in data.keys():
                    raise OdataRequestException(str(data['error']))
                return data
        except json.JSONDecodeError:
            raise OdataRequestException(f'Invalid json from {node.path.name}')
        except DrbException:
            raise OdataRequestException(f'Invalid node: {type(node)}')

    @staticmethod
    def get_type_odata_svc(service_url: str, auth: AuthBase = None) \
            -> ODataServiceType:
        """
        Retrieve with the given URL the OData service type (CSC or DHuS).

        Parameters:
            service_url (str): service URL
            auth (AuthBase): authentication mechanism required by the service
                             (default: ``None``)
        Returns:
            ODataServiceType: value corresponding to service
        """
        try:
            url = f'{service_url}/$metadata'
            node = DrbHttpNode(url, auth=auth)
            tree = ElementTree.parse(node.get_impl(io.BytesIO))
            ns = tree.getroot()[0][0].get('Namespace', None)
            if 'OData.CSC'.lower() == ns.lower():
                return ODataServiceType.CSC
            elif 'OData.DHuS'.lower() == ns.lower():
                return ODataServiceType.DHUS
            elif 'Ens'.lower() == ns.lower():
                return ODataServiceType.ONDA_DIAS
            return ODataServiceType.UNKNOWN
        except (DrbException, ParseError) as ex:
            return ODataServiceType.UNKNOWN

    @staticmethod
    def req_svc(odata: OdataNode) -> dict:
        node = DrbHttpNode(odata.get_service_url(), auth=odata.get_auth(),
                           params={'$format': 'json'})
        data = ODataUtils.http_node_to_json(node)
        return data

    @staticmethod
    def req_svc_count(odata: OdataNode) -> int:
        url = f'{odata.get_service_url()}/Products/$count'
        node = DrbHttpNode(url, auth=odata.get_auth())
        stream = node.get_impl(io.BytesIO)
        value = stream.read().decode()
        stream.close()
        return int(value)

    @staticmethod
    def req_svc_count_search(odata: OdataNode, search: str) -> int:
        url = f'{odata.get_service_url()}/Products/$count?$search={search}'
        node = DrbHttpNode(url, auth=odata.get_auth())
        stream = node.get_impl(io.BytesIO)
        value = stream.read().decode()
        stream.close()
        return int(value)

    @staticmethod
    def req_svc_products(odata: OdataNode, **kwargs) -> list:
        params = {'$format': 'json'}
        ret_count = False

        if 'filter' in kwargs.keys() and kwargs['filter'] is not None:
            params[odata.filter_keyword] = \
                kwargs['filter'].replace('\'', '%27')
        # For future use if we make search in GSS or Dhus...
        elif 'search' in kwargs.keys() and kwargs['search'] is not None:
            params[odata.filter_keyword] = kwargs['search']
        if 'order' in kwargs.keys() and kwargs['order'] is not None:
            params['$orderby'] = kwargs['order']

        if 'skip' in kwargs.keys() and kwargs['skip'] is not None:
            params['$skip'] = kwargs['skip']

        if 'top' in kwargs.keys() and kwargs['top'] is not None:
            params['$top'] = kwargs['top']

        if 'count' in kwargs.keys():
            ret_count = True
            count = kwargs['count']
            if count == -1 and odata.is_count_accepted_in_request:
                params['$count'] = 'true'

        query = '&'.join(map(lambda k: f'{k[0]}={k[1]}', params.items()))
        url = f'{odata.get_service_url()}/Products?{query}'
        node = DrbHttpNode(url, auth=odata.get_auth())
        data = ODataUtils.http_node_to_json(node)
        if ret_count:
            if '@odata.count' in data.keys():
                return data['value'], data['@odata.count']
            else:
                return data['value'], count
        return data['value']

    @staticmethod
    def req_svc_orders(odata: OdataNode, **kwargs) -> list:
        params = {'$format': 'json'}
        ret_count = False

        if 'filter' in kwargs.keys() and kwargs['filter'] is not None:
            params['filter'] = kwargs['filter'].replace('\'', '%27')
        # For future use if we make search in GSS or Dhus...
        if 'skip' in kwargs.keys() and kwargs['skip'] is not None:
            params['$skip'] = kwargs['skip']

        if 'top' in kwargs.keys() and kwargs['top'] is not None:
            params['$top'] = kwargs['top']

        if 'count' in kwargs.keys():
            ret_count = True
            count = kwargs['count']
            if count == -1:
                params['$count'] = 'true'

        query = '&'.join(map(lambda k: f'{k[0]}={k[1]}', params.items()))
        url = f'{odata.get_service_url()}/Orders?{query}'
        node = DrbHttpNode(url, auth=odata.get_auth())
        data = ODataUtils.http_node_to_json(node)
        if ret_count:
            if '@odata.count' in data.keys():
                return data['value'], data['@odata.count']
            else:
                return data['value'], count
        return data['value']

    @staticmethod
    def req_product_by_uuid(odata: OdataNode, prd_uuid: str) -> dict:
        url = f'{odata.get_service_url()}/{prd_uuid}'
        params = {'$format': 'json'}
        node = DrbHttpNode(url, auth=odata.get_auth(), params=params)
        return {
            k: v for k, v in ODataUtils.http_node_to_json(node).items()
            if not k.startswith('@odata.')
        }

    @staticmethod
    def req_product_order_by_uuid(odata):
        url = odata.path.original_path + '/Product'
        node = DrbHttpNode(url, auth=odata.parent.get_auth())
        return {
            k: v for k, v in ODataUtils.http_node_to_json(node).items()
            if not k.startswith('@odata.')
        }

    @staticmethod
    def req_product_attributes(odata: OdataNode,
                               prd_uuid: str,
                               attributes: str
                               ) -> List[dict]:
        url = f'{odata.get_service_url()}/{prd_uuid}/{attributes}'
        params = {'$format': 'json'}
        node = DrbHttpNode(url, auth=odata.get_auth(), params=params)
        data = ODataUtils.http_node_to_json(node)
        return data['value']

    @staticmethod
    def req_product_download(odata: OdataNode, prd_uuid: str, start=None,
                             end=None) -> io.BytesIO:
        url = f'{odata.get_service_url()}/{prd_uuid}/$value'
        node = DrbHttpNode(url, auth=odata.get_auth())
        if start is None or end is None:
            return node.get_impl(io.BytesIO)
        return node.get_impl(io.BytesIO, start=start, end=end)

    @staticmethod
    def launch_order(odata: OdataNode, prd_uuid: str, order: str):
        if not isinstance(prd_uuid, str):
            raise TypeError
        url = f'{odata.get_service_url()}/' \
              f'{odata.format_product(prd_uuid)}/{order}'
        node = DrbHttpNode.post(url,
                                auth=odata.get_auth())
        return node

    @staticmethod
    def get_order_by_uuid(odata: OdataNode, order_uuid: str):
        url = f'{odata.get_service_url()}/{order_uuid}'
        node = DrbHttpNode(url, auth=odata.get_auth())
        return ODataUtils.http_node_to_json(node)

    @staticmethod
    def cancel_order(odata: OdataNode, order_uuid: str):
        return DrbHttpNode.post(
            f"{odata.get_service_url()}/{order_uuid}/OData.CSC.Cancel",
            auth=odata.get_auth())


class ODataQueryPredicate(Predicate):
    """
    This predicate allowing to customize an OData query request.
    Customizable OData query elements: filter, search, orderby.

    Keyword Arguments:
        filter (str | Expression): the OData filter query element
        search (str): the OData search query element
        order (str): the OData orderby query element
    """

    def __init__(self, **kwargs):
        self.__filter = kwargs['filter'] if 'filter' in kwargs.keys() else None
        self.__search = kwargs['search'] if 'search' in kwargs.keys() else None
        self.__order = kwargs['order'] if 'order' in kwargs.keys() else None

    @property
    def filter(self) -> str:
        if isinstance(self.__filter, Expression):
            return self.__filter.evaluate()
        return self.__filter

    @property
    def order(self) -> str:
        if isinstance(self.__order, tuple):
            return f"{self.__order[0].evaluate()} {self.__order[1].evaluate()}"
        if isinstance(self.__order, list):
            order = ''
            for o in self.__order:
                order += f"{o[0].evaluate()} {o[1].evaluate()} "
            return order[:len(order)-1]
        return self.__order

    @property
    def search(self) -> str:
        return self.__search

    def matches(self, key) -> bool:
        return False

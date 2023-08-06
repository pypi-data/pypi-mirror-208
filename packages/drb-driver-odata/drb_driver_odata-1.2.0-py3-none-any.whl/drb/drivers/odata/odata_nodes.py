from __future__ import annotations

import io
import json
import time
from multiprocessing import Process
from deprecated import deprecated

from typing import Any, Dict, List, Optional, Tuple, Union

from drb.core import ParsedPath, DrbNode
from drb.exceptions.core import DrbException, DrbNotImplementationException
from drb.nodes.abstract_node import AbstractNode

from .odata_node import OdataNode
from .odata_utils import ODataUtils, ODataServiceType
from ...exceptions.odata import OdataRequestException

process = None


class ODataProductNode(OdataNode):
    def __init__(self, source: Union[OdataNode, str], product_uuid: str = None,
                 **kwargs):
        self.__initialized = False
        self.__name = None
        if isinstance(source, OdataNode):
            super().__init__(source.get_service_url(), source.get_auth())
            self.parent = source
            self.__uuid = product_uuid
        elif isinstance(source, str):
            svc_prd_id = source.split('/Products')
            auth = kwargs.get('auth', None)
            super().__init__(svc_prd_id[0], auth)
            self.__type = ODataUtils.get_type_odata_svc(svc_prd_id[0], auth)
            self.__uuid = product_uuid
        if 'data' in kwargs:
            data = kwargs['data']
            self.__uuid = data.get('Id', data.get('id'))
            self.__product = data
            self.name = data.get('Name', data.get('name'))
        self.__path = ParsedPath(
            f'{self.get_service_url()}/Products({self.__uuid})')
        self._available_impl.append(ODataProductNode)

    def format_product(self, uuid: str):
        if self.parent is not None:
            return self.parent.format_product(self.__uuid)
        if self.type_service == ODataServiceType.DHUS:
            return "Products('{0}')".format(uuid)
        return "Products({0})".format(uuid)

    @property
    def type_service(self) -> ODataServiceType:
        if self.parent is not None:
            return self.parent.type_service
        elif not hasattr(self, '__type'):
            self.__type = ODataUtils.get_type_odata_svc(self.get_service_url())
        return self.__type

    def __load_product(self):
        if not hasattr(self, ' __product'):
            self.__product = ODataUtils.req_product_by_uuid(
                self,
                self.format_product(self.__uuid))

    @property
    def name(self) -> str:
        if self.__name is None:
            self.__load_product()
            if self.type_service == ODataServiceType.ONDA_DIAS:
                self.__name = self.__product['name']
            else:
                self.__name = self.__product['Name']
        return self.__name

    @name.setter
    def name(self, value: str):
        self.__name = value

    @property
    def path(self) -> ParsedPath:
        return self.__path

    @property
    @deprecated(version='2.1.0')
    def children(self) -> List[DrbNode]:
        return [ODataProductAttributeNode(self, self.__uuid)]

    # FIXME: implemented here to ensure a complete initialization of the node
    @deprecated(version='2.1.0')
    def get_attribute(self, name: str, namespace_uri: str = None) -> Any:
        return self @ (name, namespace_uri)

    def order(self):
        if self.type_service in [
            ODataServiceType.CSC, ODataServiceType.ONDA_DIAS] and \
                self.is_online is False:
            resp = ODataUtils.launch_order(self.parent,
                                           self.get_attribute(self.parent.id),
                                           self.parent.order)
            order = ODataOrderNode(self.parent, json.loads(
                resp.value.decode()))

            return order
        else:
            raise NotImplemented()

    def has_impl(self, impl: type) -> bool:
        if impl == ODataProductNode:
            return True
        if self.type_service == ODataServiceType.ONDA_DIAS:
            online = not self.get_attribute('offline')
        else:
            online = self.get_attribute('Online')
        return online and (impl == io.BufferedIOBase or impl == io.BytesIO)

    def get_impl(self, impl: type, **kwargs) -> Any:
        if self.has_impl(impl):
            if impl == ODataProductNode:
                return self
            return ODataUtils.req_product_download(self, self.format_product(
                self.__uuid),
                                                   kwargs.get('start', None),
                                                   kwargs.get('end', None))
        raise DrbException(f'Not supported implementation: {impl}')

    def __eq__(self, other):
        if isinstance(other, ODataProductNode):
            return OdataNode.__eq__(self, other) and \
                self.__uuid == other.__uuid
        return False

    def __hash__(self):
        return hash(self._service_url)

    def __matmul__(self, other):
        self.__load_product()
        if len(self.attribute_names()) == 0:
            for k, v in self.__product.items():
                if v is not None:
                    self @= (k, None, v)
        return super().__matmul__(other)

    @property
    def is_online(self):
        if not self.attribute_names():
            self.__load_product()
        if self.type_service in [ODataServiceType.DHUS, ODataServiceType.CSC]:
            return self @ 'Online'
        elif self.type_service == ODataServiceType.ONDA_DIAS:
            return not self @ 'offline'
        return None


class ODataProductAttributeNode(OdataNode):
    __name = 'Attributes'

    def __init__(self, source: ODataProductNode, prd_uuid: str):
        super().__init__(source.get_service_url(), source.get_auth())
        self.name = self.__name
        self.parent = source
        self.__uuid = prd_uuid
        self.__attr = None
        self._available_impl.clear()

    @property
    def type_service(self) -> ODataServiceType:
        return self.parent.type_service

    def __load_attributes(self) -> None:
        if self.__attr is None:
            self.__attr = ODataUtils.req_product_attributes(
                self,
                self.parent.parent.format_product(self.__uuid),
                self.parent.parent.format_attributes()
            )

    @property
    def path(self) -> ParsedPath:
        return self.parent.path / self.__name

    @property
    def children(self) -> List[DrbNode]:
        self.__load_attributes()
        return [ODataAttributeNode(self, data=x) for x in self.__attr]

    def has_child(self, name: str = None, namespace: str = None) -> bool:
        if namespace is None:
            if name is not None:
                for x in self.__attr:
                    if name in x.keys():
                        return True
                return False
            return len(self.__attr) > 0
        return False

    def get_impl(self, impl: type, **kwargs) -> Any:
        raise DrbException(f'Do not support implementation: {impl}')


class ODataAttributeNode(OdataNode):
    def __init__(self, source: Union[str, ODataProductAttributeNode],
                 **kwargs):
        if isinstance(source, ODataProductAttributeNode):
            super().__init__(source.get_service_url(), source.get_auth())
            self.parent = source
            self._type = source.type_service
        elif isinstance(source, str):
            auth = kwargs.get('auth')
            super().__init__(source, auth)
            self._type = ODataServiceType.UNKNOWN
        else:
            raise OdataRequestException(f'Unsupported source: {type(source)}')
        self.__path = None
        self.__data = kwargs.get('data')
        for k, v in self.__data.items():
            self @= (k, None, v)
        self.name = self.__data.get('Name', self.__data.get('name'))
        self.value = self.__data.get('Value', self.__data.get('value'))
        self._available_impl.clear()

    @property
    def type_service(self) -> ODataServiceType:
        if self.parent is None:
            return ODataServiceType.UNKNOWN
        return self.parent.type_service

    @property
    def path(self) -> ParsedPath:
        if self.__path is None:
            if self.parent is None:
                self.__path = ParsedPath(self.name)
            else:
                self.__path = self.parent.path / self.name
        return self.__path

    @property
    def children(self) -> List[DrbNode]:
        return []

    def get_impl(self, impl: type, **kwargs) -> Any:
        raise DrbException(f'Do not support implementation: {impl}')


class ODataOrderNode(AbstractNode):

    def __init__(self, node: OdataNode, source: dict):
        super().__init__()
        self.name = source['Id']
        self.parent = node
        self.__path = ParsedPath(
            f'{node.get_service_url()}/{node.format_order(self.name)}')
        self._init_attributes(source)

    def __setitem__(self, key, value):
        raise NotImplementedError

    def __delitem__(self, key):
        raise NotImplementedError

    def _init_attributes(self, data):
        for k, v in data.items():
            if v is not None:
                self @= (k, None, v)

    @property
    def product(self):
        data = ODataUtils.req_product_order_by_uuid(self)
        return ODataProductNode(self.parent, data=data)

    @property
    def order_eta(self):
        return self.get_attribute(self.parent.orders_eta)

    @property
    def path(self) -> ParsedPath:
        return self.__path

    @property
    def children(self) -> List[DrbNode]:
        return []

    def get_impl(self, impl: type, **kwargs) -> Any:
        raise DrbNotImplementationException

    @property
    def status(self):
        data = ODataUtils.get_order_by_uuid(
            self.parent,
            self.parent.format_order(self.name)
        )
        self._init_attributes(data)
        return self @ 'Status'

    def cancel(self):
        if self.parent.type_service == ODataServiceType.CSC:
            return ODataUtils.cancel_order(
                self.parent, self.parent.format_order(self.name)
            )
        else:
            raise NotImplemented

    def _wait_and_check(self, order: ODataOrderNode, wait: int = 60):
        while 1:
            if not order.status != 'in_progress':
                break
            res = ODataUtils.get_order_by_uuid(
                self.parent,
                self.parent.format_order(self.name)
            )
            if res['Status'] == 'completed':
                self.product.attributes[('Online', None)] = 'True'
                break
            if res['Status'] in ['failed', 'cancelled']:
                break
            time.sleep(wait)

    def wait(self, step: int = 60):
        global process
        process = Process(target=self._wait_and_check, args=(self, step))
        process.start()
        return True

    def stop(self):
        global process
        process.terminate()

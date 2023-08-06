from __future__ import annotations

import uuid
import datetime
from abc import ABC, abstractmethod

from typing import Any, Dict, Iterable, \
    List, Optional, Tuple, Union

from drb.core import ParsedPath, DrbNode, Predicate
from drb.exceptions.core import DrbException, DrbFactoryException
from drb.topics import resolver
from requests.auth import AuthBase

from .odata_node import OdataNode
from .odata_nodes import ODataOrderNode, ODataProductNode
from .odata_utils import ODataUtils, ODataServiceType, ODataQueryPredicate


class ODataServiceNode(OdataNode, ABC):
    def __init__(self, url: str, auth: AuthBase = None):
        super(ODataServiceNode, self).__init__(url, auth)
        self.__path = ParsedPath(url)
        self._type = None

    @property
    def type_service(self) -> ODataServiceType:
        raise NotImplementedError

    @property
    def orders(self):
        raise NotImplementedError

    @property
    def orders_eta(self):
        raise NotImplementedError

    @property
    def name(self) -> str:
        return self._service_url

    @property
    def value(self) -> Optional[Any]:
        return None

    @property
    def id(self):
        raise NotImplementedError

    @property
    def order(self) -> str:
        raise NotImplementedError

    @property
    def path(self) -> ParsedPath:
        return self.__path

    @property
    def parent(self) -> Optional[DrbNode]:
        return None

    @property
    def attributes(self) -> Dict[Tuple[str, str], Any]:
        return {}

    @property
    def children(self) -> List[DrbNode]:
        filtered_list = ODataFilteredList(self)
        children_list = ODataServiceNodeList(filtered_list)
        return children_list

    def get_attribute(self, name: str, namespace_uri: str = None) -> Any:
        raise DrbException('ODataNode has no attribute')

    def has_child(self, name: str = None, namespace: str = None) -> bool:
        if namespace is None:
            if name is not None:
                try:
                    self._get_named_child(name=name)
                except DrbException:
                    return False
                return True
            return ODataUtils.req_svc_count(self) > 0
        return False

    def close(self) -> None:
        pass

    def has_impl(self, impl: type) -> bool:
        return False

    def get_impl(self, impl: type, **kwargs) -> Any:
        raise DrbException(f"ODataNot doesn't support {impl} implementation")

    @abstractmethod
    def prepare_filter(self, user_filter: str) -> str:
        raise NotImplementedError

    @abstractmethod
    def _get_named_child(self, name: str, namespace_uri: str = None,
                         occurrence: Union[int, slice] = 0) \
            -> Union[DrbNode, List[DrbNode]]:
        raise NotImplementedError

    def __retrieve_child_from_tuple(self, t: tuple) -> \
            Union[List[DrbNode], DrbNode]:
        if len(t) == 2:
            # (name, namespace)
            if t[1] is None or isinstance(t[1], str):
                return self._get_named_child(name=t[0], namespace_uri=t[1])
            # (name, occurrence)
            elif isinstance(t[1], int) or isinstance(t[1], slice):
                return self._get_named_child(t[0], occurrence=t[1])
        # (name, namespace, occurrence)
        elif len(t) == 3:
            return self._get_named_child(*t)
        raise KeyError(f'Invalid key: {t}')

    @abstractmethod
    def retrieve_default_criteria(self) -> str:
        raise NotImplementedError

    @abstractmethod
    def generate_product(self, data: dict) -> ODataProductNode:
        raise NotImplementedError

    def __retrieve_child(self, key: Union[uuid.UUID, tuple, Predicate]) -> \
            Union[List[DrbNode], DrbNode]:
        try:
            if isinstance(key, uuid.UUID):
                prd_uuid = str(key)
                data = ODataUtils.req_product_by_uuid(self,
                                                      self.format_product(
                                                          prd_uuid
                                                      ))
                return ODataProductNode(self, str(prd_uuid), data=data)
            if isinstance(key, tuple):
                return self.__retrieve_child_from_tuple(key)
            if isinstance(key, str):
                return self._get_named_child(key)
            if isinstance(key, ODataQueryPredicate):
                return ODataFilteredList(self, qfilter=key.filter,
                                         qorder=key.order)
        except DrbException as ex:
            raise KeyError from ex
        raise TypeError('Invalid type for a DrbNode bracket: '
                        f'{key.__class__}')

    def __len__(self):
        return ODataUtils.req_svc_count(self)

    def __getitem__(self, item):
        if isinstance(item, int):
            children_list = self.children
            resolved_node = children_list[item]
            return resolved_node

        elif isinstance(item, uuid.UUID):
            node = self.__retrieve_child(item)
            try:
                if node.is_online:
                    _, resolved_node = resolver.resolve(
                        node
                    )
                    return resolved_node
                else:
                    return node
            except DrbFactoryException:
                return node

        elif isinstance(item, ODataQueryPredicate):
            filtered_list = self.__retrieve_child(item)
            children_list = ODataServiceNodeList(filtered_list)
            return children_list

        elif isinstance(item, str):
            node = self.__retrieve_child(item)
            try:
                _, resolved_node = resolver.resolve(node)
                return resolved_node
            except DrbFactoryException:
                return node

        elif isinstance(item, tuple):
            node = self.__retrieve_child(item)
            try:
                _, resolved_node = resolver.resolve(node)
                return resolved_node
            except DrbFactoryException:
                return node

        elif isinstance(item, slice):
            children_list = self.children
            sliced_list = children_list[item]
            return sliced_list

        else:
            raise TypeError

    def format_product(self, uuid: str):
        raise NotImplementedError

    @property
    def format_attributes(self):
        raise NotImplementedError

    def format_order(self, uuid: str):
        raise NotImplementedError

    @property
    def filter_keyword(self) -> str:
        raise NotImplementedError

    @property
    def is_count_accepted_in_request(self) -> bool:
        raise NotImplementedError


class ODataServiceNodeCSC(ODataServiceNode):

    @property
    def id(self):
        return 'Id'

    @property
    def order(self) -> str:
        return 'OData.CSC.Order'

    @property
    def orders_eta(self) -> str:
        return 'EstimatedDate'

    @property
    def filter_keyword(self) -> str:
        return '$filter'

    @property
    def is_count_accepted_in_request(self) -> bool:
        return True

    def format_order(self, uuid: str):
        return "Orders({0})".format(uuid)

    def format_product(self, uuid: str):
        return "Products({0})".format(uuid)

    def format_attributes(self):
        return "Attributes"

    @property
    def type_service(self) -> ODataServiceType:
        self._type = ODataServiceType.CSC
        return self._type

    def retrieve_default_criteria(self) -> str:
        return 'PublicationDate'

    def prepare_filter(self, user_filter: str) -> str:
        date = datetime.datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%SZ')
        if user_filter is None:
            return f'{self.retrieve_default_criteria()} lt {date}'
        if self.retrieve_default_criteria() in user_filter:
            return user_filter
        return f"{user_filter} and" \
               f" {self.retrieve_default_criteria()} lt {date}"

    @property
    def namespace_uri(self) -> Optional[str]:
        return 'OData.CSC'

    def _get_named_child(self, name: str,
                         namespace_uri: str = None,
                         occurrence: Union[int, slice] = 0
                         ) -> Union[DrbNode, List[DrbNode]]:
        if namespace_uri is None:
            products = ODataUtils.req_svc_products(
                self, filter=f"Name eq '{name}'")
            if len(products) <= 0:
                raise DrbException(f'No child ({name}, {namespace_uri},'
                                   f' {occurrence}) found')
            p = products[occurrence]
            if isinstance(p, list):
                return [ODataProductNode(self,
                                         x['Id'], data=x) for x in p]
            return ODataProductNode(self, p['Id'], data=p)
        raise DrbException(f'No child ({name}, {namespace_uri}, {occurrence}) '
                           'found')

    @property
    def orders(self):
        return OdataOrderList(self)

    def generate_product(self, data: dict) -> ODataProductNode:
        return ODataProductNode(self, data['Id'], data=data)


class ODataServiceNodeDhus(ODataServiceNode):

    @property
    def orders(self):
        raise NotImplementedError

    @property
    def id(self):
        return 'Id'

    @property
    def order(self) -> str:
        raise NotImplementedError

    @property
    def orders_eta(self) -> str:
        raise NotImplementedError

    @property
    def filter_keyword(self) -> str:
        return '$filter'

    @property
    def is_count_accepted_in_request(self) -> bool:
        return True

    def format_order(self, uuid: str):
        return "Orders('{0}')".format(uuid)

    def format_product(self, uuid: str):
        return "Products('{0}')".format(uuid)

    def format_attributes(self):
        return "Attributes"

    @property
    def type_service(self) -> ODataServiceType:
        self._type = ODataServiceType.DHUS
        return self._type

    def retrieve_default_criteria(self) -> str:
        return 'CreationDate'

    def prepare_filter(self, user_filter: str) -> str:
        date = datetime.datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%S.0Z')
        if user_filter is None:
            return f'{self.retrieve_default_criteria()} lt {date}'
        if self.retrieve_default_criteria() in user_filter:
            return user_filter
        return f"{user_filter} and " \
               f"{self.retrieve_default_criteria()} lt {date}"

    @property
    def children(self) -> List[DrbNode]:
        return OdataFilteredListDhus(self, page_size=10)

    @property
    def namespace_uri(self) -> Optional[str]:
        return 'OData.DHuS'

    def _get_named_child(self, name: str,
                         namespace_uri: str = None,
                         occurrence: Union[int, slice] = 0
                         ) -> Union[DrbNode, List[DrbNode]]:
        if namespace_uri is None:
            products = ODataUtils.req_svc_products(
                self, filter=f"Name eq '{name}'")
            if len(products) <= 0:
                raise DrbException(f'No child ({name}, {namespace_uri},'
                                   f' {occurrence}) found')
            p = products[occurrence]
            if isinstance(p, list):
                return [ODataProductNode(self,
                                         x['Id'], data=x) for x in p]
            return ODataProductNode(self, p['Id'], data=p)
        raise DrbException(f'No child ({name}, {namespace_uri}, {occurrence}) '
                           'found')

    def __retrieve_child(self, key: Union[uuid.UUID, tuple, Predicate]) -> \
            Union[List[DrbNode], DrbNode]:
        try:
            if isinstance(key, uuid.UUID):
                prd_uuid = str(key)
                data = ODataUtils.req_product_by_uuid(self,
                                                      self.format_product(
                                                          prd_uuid
                                                      ))
                return ODataProductNode(self, str(prd_uuid), data=data)
            if isinstance(key, tuple):
                return self.__retrieve_child_from_tuple(key)
            if isinstance(key, str):
                return self._get_named_child(key)
            if isinstance(key, ODataQueryPredicate):
                return OdataFilteredListDhus(
                    self,
                    qfilter=key.filter,
                    qorder=key.order)
        except DrbException as ex:
            raise KeyError from ex
        raise TypeError('Invalid type for a DrbNode bracket: '
                        f'{key.__class__}')

    def __getitem__(self, item):
        if isinstance(item, int):
            children_list = self.children
            resolved_node = children_list[item]
            return resolved_node

        elif isinstance(item, uuid.UUID):
            node = self.__retrieve_child(item)
            try:
                if node.is_online:
                    _, resolved_node = resolver.resolve(
                        node
                    )
                    return resolved_node
                else:
                    return node
            except DrbFactoryException:
                return node

        elif isinstance(item, ODataQueryPredicate):
            filtered_list = self.__retrieve_child(item)
            children_list = ODataServiceNodeList(filtered_list)
            return children_list

        elif isinstance(item, str):
            node = self.__retrieve_child(item)
            try:
                _, resolved_node = resolver.resolve(node)
                return resolved_node
            except DrbFactoryException:
                return node

        elif isinstance(item, tuple):
            node = self.__retrieve_child(item)
            try:
                _, resolved_node = resolver.resolve(node)
                return resolved_node
            except DrbFactoryException:
                return node

        elif isinstance(item, slice):
            children_list = self.children
            sliced_list = children_list[item]
            return sliced_list

        else:
            raise TypeError

    def generate_product(self, data: dict) -> ODataProductNode:
        return ODataProductNode(self, data['Id'], data=data)


class ODataServiceNodeDias(ODataServiceNode):

    @property
    def orders(self):
        return OdataOrderList(self)

    @property
    def id(self):
        return 'id'

    @property
    def order(self) -> str:
        return 'Ens.Order'

    @property
    def orders_eta(self) -> str:
        return 'EstimatedTime'

    @property
    def filter_keyword(self) -> str:
        return '$search'

    @property
    def is_count_accepted_in_request(self) -> bool:
        return False

    def format_order(self, uuid: str):
        return "Orders('{0}')".format(uuid)

    def format_product(self, uuid: str):
        return "Products({0})".format(uuid)

    def format_attributes(self):
        return "Metadata"

    @property
    def type_service(self) -> ODataServiceType:
        self._type = ODataServiceType.ONDA_DIAS
        return self._type

    def retrieve_default_criteria(self) -> str:
        return 'creationDate'

    def prepare_filter(self, user_filter: str) -> str:
        if user_filter is None:
            return f"%22creationDate:[1900-05-10T00:00:00.000Z TO NOW]%22"
        return f"%22{user_filter}%22"

    @property
    def namespace_uri(self) -> Optional[str]:
        return 'Ens'

    def _get_named_child(self, name: str, namespace_uri: str = None,
                         occurrence: Union[int, slice] = 0
                         ) -> Union[DrbNode, List[DrbNode]]:
        if namespace_uri is None:
            products = ODataUtils.req_svc_products(
                self, search=f'"name:{name}"')
            if len(products) <= 0:
                raise DrbException(f'No child ({name}, {namespace_uri},'
                                   f' {occurrence}) found')
            p = products[occurrence]
            if isinstance(p, list):
                return [ODataProductNode(self,
                                         x['id'], data=x) for x in p]
            return ODataProductNode(self, p['id'], data=p)
        raise DrbException(f'No child ({name}, {namespace_uri}, {occurrence}) '
                           'found')

    def generate_product(self, data: dict) -> ODataProductNode:
        return ODataProductNode(self, data['id'], data=data)


class ODataFilteredList(list):

    def __init__(self, odata: OdataNode, qfilter: str = None,
                 qorder: str = None, page_size=100):
        super().__init__()
        self._count = -1
        self._page = None
        self._skip = 0
        self._page_size = page_size
        self._odata = odata
        default = odata.retrieve_default_criteria()
        self._filter = odata.prepare_filter(qfilter)
        self._order = self.__prepare_order(qorder, default)

    @classmethod
    def __prepare_order(cls, user_order: str, default: str) -> str:
        if user_order is None:
            return f'{default} desc'
        return user_order

    def __perform_query(self):
        buffer, self._count = ODataUtils.req_svc_products(
            self._odata, count=self._count, filter=self._filter,
            order=self._order, skip=self._skip, top=self._page_size)

        if self._count == -1 and not self._odata.is_count_accepted_in_request:
            self._count = ODataUtils.req_svc_count_search(self._odata,
                                                          self._filter)

        self._page = [self._odata.generate_product(e) for e in buffer]

    def __compute_index(self, item: Union[int, slice]) -> Tuple[int, int]:
        if isinstance(item, int):
            if item < 0:
                return item + len(self), -1
            return item, -1
        # item is a slice
        start = item.start if item.start is not None else 0
        if start < 0:
            start = start + len(self)
        stop = item.stop if item.stop is not None else len(self)
        if stop < 0:
            stop = stop + len(self)
        return start, stop

    def append(self, obj: Any) -> None:
        raise NotImplementedError

    def clear(self) -> None:
        raise NotImplementedError

    def copy(self) -> List[ODataProductNode]:
        raise NotImplementedError

    def count(self, value: Any) -> int:
        raise NotImplementedError

    def extend(self, iterable: Iterable[ODataProductNode]) -> None:
        raise NotImplementedError

    def index(self, value: Any, start: int = ..., stop: int = ...) -> int:
        raise NotImplementedError

    def insert(self, index: int, obj: ODataProductNode) -> None:
        raise NotImplementedError

    def pop(self, index: int = ...) -> ODataProductNode:
        raise NotImplementedError

    def remove(self, value: Any) -> None:
        raise NotImplementedError

    def reverse(self) -> None:
        raise NotImplementedError

    def sort(self: List, *, key: None = ..., reverse: bool = ...) -> None:
        raise NotImplementedError

    def __getitem_index(self, index):
        if index not in range(self._skip, self._skip + self._page_size):
            page_number = index // self._page_size
            self._skip = page_number * self._page_size
            self.__perform_query()
        return self._page[index % self._page_size]

    def __getitem__(self, item):
        if self._count == -1:
            self.__perform_query()

        if isinstance(item, int):
            index, _ = self.__compute_index(item)
            return self.__getitem_index(index)
        elif isinstance(item, slice):
            start, stop = self.__compute_index(item)
            result = []
            for index in range(start, stop):
                node = self.__getitem_index(index)
                result.append(node)
            return result
        else:
            raise KeyError(f'Invalid key: {type(item)}')

    def __iter__(self):
        def generator(qfilter, qorder, count, page_size):
            page_num = 0
            buffer = None
            for i in range(count):
                if i % page_size == 0:
                    skip = page_size * page_num
                    buffer = ODataUtils.req_svc_products(
                        self._odata, filter=qfilter, order=qorder, skip=skip,
                        top=page_size)
                    page_num += 1
                idx = i % page_size
                yield self._odata.generate_product(buffer[idx])

        return generator(self._filter, self._order, len(self), self._page_size)

    def __len__(self):
        if self._count == -1:
            self.__perform_query()
        return self._count

    def __contains__(self, item):
        raise NotImplementedError

    def __iadd__(self, other):
        raise NotImplementedError

    def __imul__(self, other):
        raise NotImplementedError


class OdataFilteredListDhus(ODataFilteredList):

    def __init__(self, odata: OdataNode, qfilter: str = None,
                 qorder: str = None, page_size=100):
        self._is_filtered = qfilter
        super().__init__(
            odata,
            qfilter,
            qorder,
            page_size)

    def __len__(self):
        if self._is_filtered is not None:
            raise IndexError('Count is not supported on this '
                             'service with filtered request.')
        if self._count == -1:
            self.__perform_query()
        return self._count

    def __perform_query(self):
        buffer = ODataUtils.req_svc_products(
            self._odata, filter=self._filter,
            order=self._order, skip=self._skip, top=self._page_size)

        if self._count == -1 and not self._odata.is_count_accepted_in_request \
                and self._is_filtered is None:
            self._count = ODataUtils.req_svc_count_search(self._odata,
                                                          self._filter)
        elif self._count == -1:
            self._count = 0

        self._count += self._page_size

        self._page = [self._odata.generate_product(e) for e in buffer]

    def __compute_index(self, item: Union[int, slice]) -> Tuple[int, int]:
        if isinstance(item, int):
            if item < 0:
                return item + self._count, -1
            return item, -1
        # item is a slice
        start = item.start if item.start is not None else 0
        if start < 0:
            start = start + self._count
        stop = item.stop if item.stop is not None else len(self)
        if stop < 0:
            stop = stop + self._count
        return start, stop

    def __iter__(self):
        def generator(qfilter, qorder, count, page_size):
            page_num = 0
            buffer = None
            for i in range(count):
                if i % page_size == 0:
                    skip = page_size * page_num
                    buffer = ODataUtils.req_svc_products(
                        self._odata, filter=qfilter, order=qorder, skip=skip,
                        top=page_size)
                    page_num += 1
                idx = i % page_size
                yield self._odata.generate_product(buffer[idx])

        return generator(self._filter, self._order,
                         self._count, self._page_size)


class OdataOrderList(list):
    def __init__(self, odata: ODataServiceNode, qfilter: str = None,
                 page_size=100):
        super().__init__()
        self._count = -1
        self._page = None
        self._skip = 0
        self._page_size = page_size
        self._filter = qfilter
        self._odata = odata

    def __perform_query(self):
        buffer, self._count = ODataUtils.req_svc_orders(
            self._odata, count=self._count,
            filter=self._filter,
            skip=self._skip,
            top=self._page_size)

        self._page = [ODataOrderNode(self._odata, e) for e in buffer]

    def __compute_index(self, item: Union[int, slice]) -> Tuple[int, int]:
        if isinstance(item, int):
            if item < 0:
                return item + len(self), -1
            return item, -1
        # item is a slice
        start = item.start if item.start is not None else 0
        if start < 0:
            start = start + len(self)
        stop = item.stop if item.stop is not None else len(self)
        if stop < 0:
            stop = stop + len(self)
        return start, stop

    def append(self, obj: Any) -> None:
        raise NotImplementedError

    def clear(self) -> None:
        raise NotImplementedError

    def copy(self) -> List[ODataProductNode]:
        raise NotImplementedError

    def count(self, value: Any) -> int:
        raise NotImplementedError

    def extend(self, iterable: Iterable[ODataProductNode]) -> None:
        raise NotImplementedError

    def index(self, value: Any, start: int = ..., stop: int = ...) -> int:
        raise NotImplementedError

    def insert(self, index: int, obj: ODataProductNode) -> None:
        raise NotImplementedError

    def pop(self, index: int = ...) -> ODataProductNode:
        raise NotImplementedError

    def remove(self, value: Any) -> None:
        raise NotImplementedError

    def reverse(self) -> None:
        raise NotImplementedError

    def sort(self: List, *, key: None = ..., reverse: bool = ...) -> None:
        raise NotImplementedError

    def __getitem_index(self, index):
        if index not in range(self._skip, self._skip + self._page_size):
            page_number = index // self._page_size
            self._skip = page_number * self._page_size
            self.__perform_query()
        return self._page[index % self._page_size]

    def __getitem__(self, item):
        if isinstance(item, uuid.UUID):
            order_uuid = str(item)
            data = ODataUtils.get_order_by_uuid(self._odata,
                                                self._odata.format_order(
                                                    order_uuid
                                                ))
            return ODataOrderNode(self._odata, source=data)

        if self._count == -1:
            self.__perform_query()

        if isinstance(item, int):
            index, _ = self.__compute_index(item)
            return self.__getitem_index(index)
        elif isinstance(item, slice):
            start, stop = self.__compute_index(item)
            result = []
            for index in range(start, stop):
                node = self.__getitem_index(index)
                result.append(node)
            return result
        elif isinstance(item, ODataQueryPredicate):
            return OdataOrderList(self._odata, qfilter=item.filter)
        else:
            raise KeyError(f'Invalid key: {type(item)}')

    def __iter__(self):
        def generator(count, page_size):
            page_num = 0
            buffer = None
            for i in range(count):
                if i % page_size == 0:
                    skip = page_size * page_num
                    buffer = ODataUtils.req_svc_orders(
                        self._odata, skip=skip,
                        top=page_size)
                    page_num += 1
                idx = i % page_size
                yield ODataOrderNode(self._odata, buffer[idx])

        return generator(len(self), self._page_size)

    def __len__(self):
        if self._count == -1:
            self.__perform_query()
        return self._count

    def __contains__(self, item):
        raise NotImplementedError

    def __iadd__(self, other):
        raise NotImplementedError

    def __imul__(self, other):
        raise NotImplementedError


class ODataServiceNodeList(list):

    def __init__(self, odata: Union[List[DrbNode], ODataFilteredList]):
        super().__init__()
        self._odata = odata

    def __getitem__(self, item):

        if isinstance(item, slice):
            sliced_list = self._odata[item]
            result = ODataServiceNodeList(sliced_list)
            return result

        elif isinstance(item, int):
            node = self._odata[item]
            try:
                if node.is_online:
                    _, resolved_node = resolver.resolve(
                        node
                    )
                    return resolved_node
                else:
                    return node
            except DrbFactoryException:
                return node
        else:
            raise KeyError(f'Invalid key: {type(item)}')

    def __iter__(self):
        def gen():
            i = 0
            while 1:
                try:
                    node = self._odata[i]
                    try:
                        _, resolved_node = resolver.resolve(node)
                    except DrbFactoryException:
                        return node
                    yield resolved_node
                    i += 1
                except IndexError:
                    break

        return gen()

    def __len__(self):
        count = len(self._odata)
        return count

    def append(self, obj: Any) -> None:
        raise NotImplementedError

    def clear(self) -> None:
        raise NotImplementedError

    def copy(self) -> List[ODataProductNode]:
        raise NotImplementedError

    def count(self, value: Any) -> int:
        raise NotImplementedError

    def extend(self, iterable: Iterable[ODataProductNode]) -> None:
        raise NotImplementedError

    def index(self, value: Any, start: int = ..., stop: int = ...) -> int:
        raise NotImplementedError

    def insert(self, index: int, obj: ODataProductNode) -> None:
        raise NotImplementedError

    def pop(self, index: int = ...) -> ODataProductNode:
        raise NotImplementedError

    def remove(self, value: Any) -> None:
        raise NotImplementedError

    def reverse(self) -> None:
        raise NotImplementedError

    def sort(self: List, *, key: None = ..., reverse: bool = ...) -> None:
        raise NotImplementedError

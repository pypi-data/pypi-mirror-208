import io
import json
import keyring

from requests.auth import HTTPBasicAuth
from drb.core import DrbFactory, DrbNode
from drb.drivers.http import DrbHttpNode
from drb.drivers.json import JsonNode
from drb.exceptions.core import DrbFactoryException
from .odata_node import OdataNode
from .odata_nodes import ODataProductNode
from .odata_services_nodes import ODataServiceNodeDhus, \
    ODataServiceNodeDias, ODataServiceNodeCSC
from .odata_utils import ODataServiceType, ODataUtils


class OdataFactory(DrbFactory):
    def _create(self, node: DrbNode) -> DrbNode:
        if isinstance(node, OdataNode):
            return node
        if isinstance(node, DrbHttpNode):
            if '$format=json' not in node.path.original_path:
                if '?' not in node.path.original_path:
                    node._path = node.path.original_path + '?&$format=json'
                else:
                    node._path = node.path.original_path + '&$format=json'
            req = node.get_impl(io.BytesIO).read().decode()
            json_node = JsonNode(json.loads(req))
            return [ODataProductNode(source=node.path.original_path,
                                     auth=node.auth,
                                     data=e.value
                                     ) for e in json_node['value', :]]
        final_url = node.path.name.replace('+odata', '')

        auth = keyring.get_keyring().get_credential(final_url, None)
        if auth is not None:
            auth = HTTPBasicAuth(auth.username, auth.password)

        service_type = ODataUtils.get_type_odata_svc(final_url, auth)
        if service_type == ODataServiceType.CSC:
            return ODataServiceNodeCSC(final_url, auth)
        if service_type == ODataServiceType.DHUS:
            return ODataServiceNodeDhus(final_url, auth)
        if service_type == ODataServiceType.ONDA_DIAS:
            return ODataServiceNodeDias(final_url, auth)

        raise DrbFactoryException(f'Unsupported Odata service: {final_url}')

import abc
import keyring
from drb.nodes.abstract_node import AbstractNode
from requests.auth import AuthBase, HTTPBasicAuth
from typing import Optional


class OdataNode(AbstractNode, abc.ABC):
    """
    Common ODataNode interface
    """

    def __init__(self, service_url, auth: AuthBase = None):
        super(OdataNode, self).__init__()
        self._original_service_url = service_url
        self._service_url = service_url.replace('+odata', '') \
            if '+odata' in service_url else service_url
        self.__auth = auth

    def get_service_url(self) -> str:
        """
        Returns URL of the OData service.
        :returns: string URL representation the OData service
        :rtype: str
        """
        return self._service_url

    def get_auth(self) -> Optional[AuthBase]:
        """
        Returns the associated authentication required to access to the OData
        service.
        :returns: an authentication compatible with requests library.
        :rtype: AuthBase
        """
        if self.__auth is None:
            auth = keyring.get_keyring().get_credential(
                self._original_service_url, None)
            if auth is not None:
                self.__auth = HTTPBasicAuth(auth.username, auth.password)
        return self.__auth

    @property
    @abc.abstractmethod
    def type_service(self):
        raise NotImplementedError

    def __eq__(self, other):
        return isinstance(other, OdataNode) and \
            self._service_url == other._service_url

    def __hash__(self):
        return hash(self._service_url)

    def __setitem__(self, key, value):
        raise NotImplementedError

    def __delitem__(self, key):
        raise NotImplementedError

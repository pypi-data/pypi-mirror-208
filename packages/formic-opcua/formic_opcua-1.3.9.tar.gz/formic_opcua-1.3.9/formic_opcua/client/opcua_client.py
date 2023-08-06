# Copyright Formic Technologies 2023
import logging
import warnings
from asyncio.exceptions import TimeoutError
from datetime import datetime
from typing import Any, Dict, List, Tuple

from asyncua import Node
from asyncua.sync import Client, ThreadLoopNotRunning
from asyncua.ua import NodeClass
from asyncua.ua.uatypes import DataValue, DateTime, Variant

from formic_opcua.core import InvalidClientArgsError, convert_type, parse_settings

logger = logging.getLogger(__name__)
warnings.simplefilter('error')


class OpcuaClient:
    def __init__(
        self, server_config_file: str = None, url: str = None, uri: str = None, connect_timeout: float = 0.25
    ) -> None:
        if server_config_file is None and (url is None and uri is None):
            error_message = 'No configuration arguments passed to client.'
            logger.critical(error_message)
            raise InvalidClientArgsError(error_message)

        if server_config_file is not None and (url is not None or uri is not None):
            error_message = (
                'Conflicting arguments passed to client. Either pass a value for server_config_file or for url and uri.'
                'Do not pass arguments for server_config_file and url+uri at the same time.'
            )
            logger.critical(error_message)
            raise InvalidClientArgsError(error_message)

        logger.debug('Configuring client.')
        self._server_config_file = server_config_file

        if server_config_file is not None:
            self.config = parse_settings(self._server_config_file)
            self._url = self.config['server_settings']['url']
            self._uri = self.config['server_settings']['uri']
        else:
            self._url = url
            self._uri = uri

        self._idx = -1
        self._node_path_list: List[str] = []
        self._client = Client(url=self._url)
        self.connect_timeout = connect_timeout
        self._has_connected = False
        self._node_map: Dict[str, Tuple] = {}
        self._identifier_map: Dict[str, List[str]] = {}

        logger.info(f'Client created with url: {self._url}, and uri: {self._uri}')

    def __enter__(self):
        self._connect()
        self._establish_server_structure()
        return self

    def __exit__(self, *args) -> None:
        self._disconnect()

    def _connect(self):
        try:
            if self._test_server_connection():
                logger.info('_connect called but there is a connection to the server.')
                self._has_connected = True
                return
            if self._disconnect():
                self._client = Client(url=self._url, timeout=self.connect_timeout)
            logger.info('Connecting...')
            self._client.connect()
            logger.info('Connected...')
            self._has_connected = True
        except (ConnectionRefusedError, ConnectionError, RuntimeError, RuntimeWarning, TimeoutError):
            logger.error(
                f'Unable to connect to server. Client expects server to have url: {self._url} and uri: {self._uri}. '
                f'Server is not running or the configs are not matched with client.'
            )
            self._has_connected = False

    def _disconnect(self) -> bool:
        logger.info('Cleaning up client.')
        try:
            self._client.disconnect()
            return True
        except (RuntimeError, ConnectionError, ThreadLoopNotRunning):
            logger.warning('Tried to disconnect but there is no connection.')
            return False

    def _dfs_mapper(self, node: Node, path: str):
        # if node.read_node_class() == NodeClass.Variable and node.NamespaceIndex == self._idx:
        browse_path = node.read_browse_name()
        node_class = node.read_node_class()
        path_to_node = path + '/' + browse_path.Name
        if node_class == NodeClass.Variable and browse_path.NamespaceIndex == self._idx:
            # Remove "/Objects/" since this client is intended for reading only custom nodes
            path_to_node = path_to_node[9:]
            var_type = node.read_data_type_as_variant_type()
            logger.info(f'Found OPCUA variable {path_to_node}, of variant type {var_type}')
            if not path_to_node.startswith('/'):
                self._node_map['/' + path_to_node] = (node, var_type)
            else:
                self._node_map[path_to_node] = (node, var_type)

        for child_node in node.get_children():
            self._dfs_mapper(child_node, path_to_node)

    def _establish_server_structure(self) -> None:
        try:
            logger.info(f'Mapping namespace using {self._url} and {self._uri}')
            self._idx = self._client.get_namespace_index(self._uri)
            logger.info(f'Namespace index = {self._idx}')
            root_object_node = self._client.nodes.root.get_child(['0:Objects'])
            self._dfs_mapper(node=root_object_node, path='')
            self._node_path_list = list(self._node_map.keys())
            logger.info(f'All nodes successfully mapped: {self._node_path_list}')
        except (AttributeError, ConnectionError, RuntimeWarning, ValueError, ThreadLoopNotRunning):
            logger.error(f'Unable to map opcua nodes from {self._url} and {self._uri}')

    def _test_server_connection(self) -> bool:
        try:
            self._client.get_namespace_index(self._uri)
            return True
        except Exception as e:
            logger.warning(e)
            logger.warning('Failed server connectivity test.')
            return False

    def _write_helper(self, path: str, value: Any) -> bool:
        if self._has_connected:
            try:
                var, var_type = self._node_map[path]
            except KeyError:
                logger.warning(f'Unable to find {path} in client map {self._node_map}')
                return False
            try:
                value = convert_type(value=value, var_type=var_type)
            except (KeyError, TypeError):
                logger.warning(f'Unable to convert value {value} to variant type {var_type}')
                return False
            try:
                current_time: DateTime = datetime.utcnow()  # type: ignore
                var.write_value(
                    DataValue(
                        Value=Variant(value, var_type),
                        SourceTimestamp=current_time,
                        ServerTimestamp=current_time,
                    )
                )
                logger.info(f'Wrote value {value} of type {var_type} to {path}')
                return True
            except (ConnectionError, ThreadLoopNotRunning) as e:
                logger.warning(f'{e}')
                logger.warning(f'Unable to write value {value} of type {var_type} to {path}')
        else:
            logger.warning(f'No connection has been made to server. Cannot write value {value} to path {path}')
        return False

    def write(self, path: str, value: Any) -> bool:
        logger.info(f'Attempting to write value {value} to path {path}.')
        if not self._has_connected:  # Write attempt has failed or client never connected.
            logger.info('Client has not connected to server. Attempting to connect.')
            self.__enter__()
        if self._write_helper(path=path, value=value):
            logger.info('Write attempt succeeded')
            return True
        else:
            logger.warning('Write attempt failed')
            self._has_connected = False

        return False

    def _read_helper(self, path: str, return_datavalue: bool = False) -> Any:
        if self._has_connected:
            try:
                node = self._node_map[path][0]
            except (KeyError, IndexError):
                logger.warning(f'Unable to get node {path} from client map {self._node_map}')
                return None
            try:
                value = node.read_value() if not return_datavalue else node.read_data_value()
                logger.info(f'Read value {value} from path {path}')
                return value
            except (ConnectionError, ThreadLoopNotRunning) as e:
                logger.warning(f'{e}')
                logger.warning(f'Unable to read node at {path}')
        else:
            logger.warning(f'No connection has been made to server. Cannot read node at path {path}')
        return None

    def read(self, path: str, return_datavalue: bool = False) -> Any:
        logger.info(f'Attempting to read path {path}.')
        if not self._has_connected:  # Read attempt has failed or client never connected.
            logger.info('Client has not connected to server. Attempting to connect.')
            self.__enter__()
        value = self._read_helper(path=path, return_datavalue=return_datavalue)
        if value is not None:
            logger.info('Read attempt succeeded')
            logger.info(f'Value: {value}')
            return value
        else:
            logger.warning('Read attempt failed')
            self._has_connected = False
        return None

    def read_all(self, return_datavalue: bool = False) -> Dict[str, Any]:
        logger.info(f'Attempting to read all variables on server at uri: {self._uri} and url: {self._url}.')
        results = {}
        if not self._has_connected:  # Client has never successfully connected to the server
            logger.info('Client may not be connected to server. Attempting to connect.')
            self.__enter__()  # Creates a new client object and adjusts self._has_connected() appropriately
        if self._has_connected:  # In case self.__enter__() changed value to true by establishing a connection
            for path in self._node_path_list:
                value = self._read_helper(path, return_datavalue=return_datavalue)
                if value is not None:
                    logger.info(f'Successfully read value: {value} for path: {path}')
                    results[path] = value
                else:
                    # This could happens if there is a disconnect during reading
                    logger.warning(f'Unsuccessful read attempt for path {path}')
                    self._has_connected = False
                    break

        if len(self._node_path_list) == 0 or len(results) != len(self._node_path_list):
            # Either there was never a connection or there was a disconnect
            # while reading and only some results were read
            self._has_connected = False
        logger.info(f'{results}')
        return results

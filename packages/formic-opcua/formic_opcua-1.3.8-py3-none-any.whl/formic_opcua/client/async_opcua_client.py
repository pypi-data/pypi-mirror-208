# Copyright Formic Technologies 2023
import asyncio
import logging
import warnings
from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Tuple

from asyncua import Client, Node
from asyncua.ua import NodeClass
from asyncua.ua.uatypes import DataValue, DateTime, Variant

from formic_opcua.core import InvalidClientArgsError, convert_type, parse_settings

logger = logging.getLogger(__name__)
warnings.simplefilter('error')


class ConnectionStatus(Enum):
    CONNECTED = 0
    CONNECTING = 1
    DISCONNECTED = 2


class AsyncOpcuaClient:
    def __init__(
        self,
        server_config_file: str = None,
        connect_timeout: float = 0.5,
        url: str = None,
        uri: str = None,
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
        self._connection_status = ConnectionStatus.DISCONNECTED
        self._node_map: Dict[str, Tuple] = {}

        logger.info(f'Client created with url: {self._url}, and uri: {self._uri}')

    async def __aenter__(self):
        if self._connection_status != ConnectionStatus.CONNECTING:
            self._connection_status = ConnectionStatus.CONNECTING
            await self._connect()
            await self._establish_server_structure()
            self._connection_status = ConnectionStatus.CONNECTED
            return self

    async def __aexit__(self, *args) -> None:
        await self._disconnect()

    async def _connect(self):
        try:
            # if await self._test_server_connection():
            #     logger.info('_connect called but there is a connection to the server.')
            #     self._connection_status =
            #     return
            if await self._disconnect():
                self._client = Client(url=self._url, timeout=self.connect_timeout)
            logger.info('Connecting...')
            await self._client.connect()
            logger.info('Connected...')
        except (ConnectionRefusedError, ConnectionError, RuntimeError, RuntimeWarning, TimeoutError):
            logger.error(
                f'Unable to connect to server. Client expects server to have url: {self._url} and uri: {self._uri}. '
                f'Server is not running or the configs are not matched with client.'
            )
            self._connection_status = ConnectionStatus.DISCONNECTED
        except Exception as e:
            logger.error(
                'Unhandled exception while to connecting to server. '
                f'Client expects server to have url: {self._url} and uri: {self._uri}. '
                f'{e}'
            )
            self._connection_status = ConnectionStatus.DISCONNECTED

    async def _disconnect(self) -> bool:
        logger.info('Cleaning up client.')
        try:
            await self._client.disconnect()
            return True
        except (RuntimeError, ConnectionError):
            logger.warning('Tried to disconnect but there is no connection.')
            return False
        except Exception as e:
            logger.error(f'Unhandled exception while to disconnecting from server. {e} ')
            return False

    async def _dfs_mapper(self, node: Node, path: str) -> None:
        browse_path = await node.read_browse_name()

        if browse_path.NamespaceIndex != self._idx and browse_path.NamespaceIndex != 0:
            return

        node_class = await node.read_node_class()
        path_to_node = path + '/' + browse_path.Name

        # if node_class == NodeClass.Variable and browse_path.NamespaceIndex == self._idx:
        if node_class == NodeClass.Variable:
            # Remove "/Objects/" since this client is intended for reading only custom nodes
            if path_to_node.startswith('/Objects/'):
                path_to_node = path_to_node[9:]
            var_type = await node.read_data_type_as_variant_type()
            logger.info(f'Found OPCUA variable {path_to_node}, of variant type {var_type}')
            if not path_to_node.startswith('/'):
                self._node_map['/' + path_to_node] = (node, var_type)
            else:
                self._node_map[path_to_node] = (node, var_type)
            return

        child_node_list = []
        node_children = await node.get_children()

        for child_node in node_children:
            child_node_list.append(self._dfs_mapper(child_node, path_to_node))

        await asyncio.gather(*child_node_list)
        return

    async def _establish_server_structure(self) -> None:
        try:
            logger.info(f'Mapping namespace using {self._url} and {self._uri}')
            self._idx = await self._client.get_namespace_index(self._uri)
            logger.info(f'Namespace index = {self._idx}')
            root_object_node = await self._client.nodes.root.get_child(['0:Objects'])
            await self._dfs_mapper(node=root_object_node, path='')

            self._node_path_list = list(self._node_map.keys())
            logger.info(f'All nodes successfully mapped: {self._node_path_list}')
        except (AttributeError, ConnectionError, RuntimeWarning, ValueError):
            logger.error(f'Unable to map opcua nodes from {self._url} and {self._uri}')
        except Exception as e:
            logger.error(f'Unhandled exception while to mapping server structure. {e}')

    async def _test_server_connection(self) -> bool:
        try:
            await self._client.get_namespace_index(self._uri)
            return True
        except Exception as e:
            logger.warning(e)
            logger.warning('Failed server connectivity test.')
            return False

    async def _write_helper(self, path: str, value: Any) -> bool:
        try:
            var, var_type = self._node_map[path]
        except KeyError:
            logger.warning(f'Unable to find {path} in client map {self._node_map}')
            return False
        try:
            value = convert_type(value=value, var_type=var_type)
        except (KeyError, TypeError, Exception):
            logger.warning(f'Unable to convert value {value} to variant type {var_type}')
            return False
        try:
            current_time: DateTime = datetime.utcnow()
            await var.write_value(
                DataValue(
                    Value=Variant(value, var_type),
                    SourceTimestamp=current_time,
                    ServerTimestamp=current_time,
                )
            )
            logger.info(f'Wrote value {value} of type {var_type} to {path}')
            return True
        except ConnectionError as e:
            logger.warning(f'{e}')
            logger.warning(f'Unable to write value {value} of type {var_type} to {path}')
        return False

    async def write(self, path: str, value: Any) -> bool:
        logger.info(f'Attempting to write value {value} to path {path}.')
        if self._connection_status == ConnectionStatus.DISCONNECTED:
            # Write attempt has failed or client never connected.
            logger.info('Client has not connected to server. Attempting to connect.')
            await self.__aenter__()
        if self._connection_status == ConnectionStatus.CONNECTED:
            if await self._write_helper(path=path, value=value):
                logger.info('Write attempt succeeded')
                return True
            else:
                logger.warning('Write attempt failed')
                self._connection_status = ConnectionStatus.DISCONNECTED
        return False

    async def _read_helper(self, path: str) -> Any:
        try:
            node = self._node_map[path][0]
        except (KeyError, IndexError):
            logger.warning(f'Unable to get node {path} from client map {self._node_map}')
            return None
        try:
            value = await node.read_value()
            logger.info(f'Read value {value} from path {path}')
            return value
        except Exception as e:
            logger.warning(f'{e}')
            logger.warning(f'Unable to read node at {path}')
        return None

    async def read(self, path: str) -> Any:
        logger.info(f'Attempting to read path {path}.')
        if self._connection_status == ConnectionStatus.DISCONNECTED:
            # Read attempt has failed or client never connected.
            logger.info('Client has not connected to server. Attempting to connect.')
            await self.__aenter__()
        if self._connection_status == ConnectionStatus.CONNECTED:
            value = await self._read_helper(path=path)
            if value is not None:
                logger.info('Read attempt succeeded')
                logger.info(f'Value: {value}')
                return value
            else:
                logger.warning('Read attempt failed')
                self._connection_status = ConnectionStatus.DISCONNECTED
        return None

    async def read_all(self, prefix: str = '') -> Dict[str, Any]:
        logger.info(f'Attempting to read all variables on server at uri: {self._uri} and url: {self._url}.')
        results = {}
        future_results = {}

        if self._connection_status == ConnectionStatus.DISCONNECTED:
            logger.info('Client may not be connected to server. Attempting to connect.')
            await self.__aenter__()  # Creates a new client object and adjusts self._has_connected() appropriately

        if self._connection_status == ConnectionStatus.CONNECTED:
            for path in self._node_path_list:
                if path.startswith(prefix):
                    task_value = asyncio.create_task(self._read_helper(path))
                    future_results[path] = task_value

        if len(self._node_path_list) == 0:
            # There may never have been a connection
            self._connection_status = ConnectionStatus.DISCONNECTED

        await asyncio.gather(*future_results.values())

        for path, task in future_results.items():
            task_value = task.result()

            if task_value is not None:
                logger.info(f'Successfully read value: {task_value} for path: {path}')
            else:
                # This could happens if there is a disconnect during reading
                logger.warning(f'Unsuccessful read attempt for path {path}')
                self._connection_status = ConnectionStatus.DISCONNECTED
            results[path] = task_value

        logger.info(f'{results}')
        return results

    def identifier_from_string(self, path: str) -> List[str]:
        identifier = [f'{self._idx}:{path_part}' for path_part in path.split('/')]
        return ['0:Objects'] + identifier

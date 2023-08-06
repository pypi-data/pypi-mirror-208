# Copyright Formic Technologies 2023
import asyncio
import logging
import posixpath
import warnings
from datetime import datetime
from typing import Dict, Optional, Union

from asyncua import Server
from asyncua.common import Node
from asyncua.ua.uatypes import DataValue, DateTime, SecurityPolicyType, Variant, VariantType

from formic_opcua.core import parse_settings

warnings.simplefilter('error')
logger = logging.getLogger(__name__)


class OpcuaServer:
    def __init__(self, server_config_file: str) -> None:
        logger.info('Initializing server.')
        self._server = Server()
        self.objects: Dict[str, Node] = dict()
        self.config: Dict[str, dict] = parse_settings(server_config_file)
        self.settings: Dict[str, str] = self.config['server_settings']
        self.root_object: Optional[Node] = None
        self._idx: int = -1

    async def run(self) -> None:
        self.root_object = self._server.nodes.objects
        self.objects[''] = self.root_object
        for child_root_name, child_root in self.config['opcua_nodes'].items():
            await self.populate_opcua_nodes(
                root_name=child_root_name,
                parent_path='',
                root=child_root,
                parent_object=self.root_object,
            )
        logger.debug(self.objects)
        await self._server.start()

    async def configure(self) -> None:
        try:
            logger.info('Configuring server.')
            await self._server.init()
            logger.debug('Server initialized.')
            self._server.set_endpoint(url=self.settings['url'])
            logger.debug(f"Server endpoint set to: {self.settings['url']}")
            self._server.set_server_name(name=self.settings['server_name'])
            logger.debug(f"Setting server name to: {self.settings['server_name']}")
            logger.debug('Setting security policy.')
            self._server.set_security_policy(security_policy=(SecurityPolicyType.NoSecurity,))
            self._server.set_security_IDs(policy_ids=('Anonymous',))
            self._idx = await self._server.register_namespace(uri=self.settings['uri'])
            logger.debug(f"Registered server namespace: {self.settings['uri']}")
            logger.info('Server configuration finished successfully')
        except Exception as e:
            logger.error(f'Server configuration failed. {repr(e)}')

    async def populate_opcua_nodes(
        self,
        root_name: str,
        parent_path: str,
        root: dict,
        parent_object: Node,
    ) -> None:
        if self._is_leaf(root):
            await self._add_variable(
                variable=root_name,
                path=parent_path,
                initial_value=root['initial_value'],
                var_type=root['type'],
            )
            return None
        parent_path = posixpath.join(parent_path, root_name)
        if parent_path not in self.objects:
            parent_object = await parent_object.add_object(
                nodeid=self._idx,
                bname=root_name,
            )
            self.objects[parent_path] = parent_object
        for child_root_name, child_root in root.items():
            await self.populate_opcua_nodes(
                root_name=child_root_name,
                parent_path=parent_path,
                root=child_root,
                parent_object=parent_object,
            )

    async def _add_variable(
        self,
        variable: str,
        path: str,
        initial_value: Union[int, float, str, bool],
        var_type: str,
    ) -> None:
        logger.debug(f'Adding {path}/{variable}')
        opcua_variable = await self.objects[path].add_variable(
            nodeid=self._idx,
            bname=variable,
            val=initial_value,
            varianttype=getattr(VariantType, var_type),
        )
        await opcua_variable.set_writable()
        logger.debug(f'{variable} set to writeable')
        await asyncio.sleep(0.1)
        current_time: DateTime = datetime.utcnow()  # type: ignore
        logger.debug(f'Setting source and server timestamp to {current_time}')
        await opcua_variable.write_value(
            DataValue(
                Value=Variant(initial_value, getattr(VariantType, var_type)),
                SourceTimestamp=current_time,
                ServerTimestamp=current_time,
            ),
        )
        logger.info(f'Successfully added {path}/{variable}')

    @staticmethod
    def _is_leaf(root: dict) -> bool:
        if 'initial_value' in root:
            return True
        return False

    async def stop(self) -> None:
        await self._server.stop()

    async def launch(self) -> None:
        await self.configure()
        await self.run()

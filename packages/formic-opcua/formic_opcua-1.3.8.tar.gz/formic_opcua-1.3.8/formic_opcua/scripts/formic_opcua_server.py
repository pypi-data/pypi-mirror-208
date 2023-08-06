# Copyright Formic Technologies 2023
import asyncio
import logging
import sys
from argparse import ArgumentParser
from typing import Union

from yaml.scanner import ScannerError

from formic_opcua import OpcuaServer

logging.basicConfig(
    stream=sys.stdout,
    level=logging.DEBUG,
    format='%(asctime)s | %(levelname)s | %(name)s | %(module)s | %(funcName)s:%(lineno)d | %(message)s',
)


def get_server(config_path: str) -> Union[OpcuaServer, None]:
    try:
        return OpcuaServer(server_config_file=config_path)
    except (FileNotFoundError, ScannerError):
        return None


async def launch_server(server: OpcuaServer) -> None:
    await server.configure()
    await server.run()


async def stop_server(server: OpcuaServer) -> None:
    await server.stop()


def main():
    parser = ArgumentParser(
        description='Run OPC UA server based on provided configuration',
        epilog='Formic Automation Solutions: https://formic.co/',
    )
    parser.add_argument(
        '-c',
        '--config',
        required=True,
        help='path to YAML configuration file',
    )
    args = parser.parse_args()

    loop = asyncio.get_event_loop()

    if server := get_server(config_path=args.config):
        try:
            loop.create_task(launch_server(server))
            loop.run_forever()
        except KeyboardInterrupt:
            loop.run_until_complete(stop_server(server))
        finally:
            loop.close()


if __name__ == '__main__':
    main()

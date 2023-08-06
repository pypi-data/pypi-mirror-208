# Copyright Formic Technologies 2023
import logging
import sys
from argparse import ArgumentParser
from typing import Union

from yaml.scanner import ScannerError

from formic_opcua import OpcuaClient

asyncua_logger = logging.getLogger('asyncua')
asyncua_logger.setLevel(logging.ERROR)
logging.basicConfig(
    stream=sys.stdout,
    level=logging.DEBUG,
    format='%(asctime)s | %(levelname)s | %(name)s | %(module)s | %(funcName)s:%(lineno)d | %(message)s',
)


def get_client(config_path: str) -> Union[OpcuaClient, None]:
    try:
        return OpcuaClient(server_config_file=config_path)
    except (FileNotFoundError, ScannerError):
        return None


def main():
    parser = ArgumentParser(
        description='Initialize OPC UA client based on provided configuration and send ',
        epilog='Formic Automation Solutions: https://formic.co/',
    )
    parser.add_argument(
        '-c',
        '--config',
        required=True,
        help='path to YAML configuration file',
    )
    parser.add_argument(
        '-p',
        '--path',
        required=True,
        help='OPC UA node browse path',
    )
    parser.add_argument(
        '-v',
        '--value',
        required=True,
        help='value to be set to node',
    )
    args = parser.parse_args()

    if client := get_client(config_path=args.config):
        try:
            client.connect()
            client.write(
                path=args.path,
                value=args.value,
            )
        finally:
            client.disconnect()


if __name__ == '__main__':
    main()

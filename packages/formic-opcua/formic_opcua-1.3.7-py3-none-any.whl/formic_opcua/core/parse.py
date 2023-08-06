# Copyright Formic Technologies 2023
import logging
from typing import Union

import yaml
from yaml.loader import SafeLoader
from yaml.scanner import ScannerError

from .exceptions import InvalidYamlError

logger = logging.getLogger(__name__)


def parse_settings(server_config_file: str) -> Union[dict, None]:
    try:
        logger.info(f'Parsing settings from {server_config_file}')
        with open(server_config_file, 'r') as config_file:
            yaml_settings = yaml.load(
                stream=config_file,
                Loader=SafeLoader,
            )
            if not isinstance(yaml_settings, dict):
                logger.error(f'Parsed server config is not a dictionary: {yaml_settings}')
                raise InvalidYamlError
            logger.debug(f'Parsed server config: {yaml_settings}')
            return yaml_settings

    except FileNotFoundError as e:
        logger.critical(e)
        raise e

    except ScannerError:
        yaml_error = InvalidYamlError('Server config file is not in proper yaml format.')
        logger.critical(yaml_error)
        raise yaml_error

    return None

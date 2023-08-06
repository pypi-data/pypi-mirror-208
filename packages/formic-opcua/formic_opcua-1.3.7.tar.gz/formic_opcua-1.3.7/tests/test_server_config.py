# Copyright Formic Technologies 2023
import os
from unittest import TestCase

from formic_opcua.core import InvalidYamlError, parse_settings


class TestOpcuaServer(TestCase):
    def test_parse_settings_yaml_typo(self):
        with open('temp_bad_server_config.yaml', 'w') as f:
            f.write('NOT YAML FORMAT.\nabc:')
        with self.assertRaises(InvalidYamlError):
            parse_settings('temp_bad_server_config.yaml')
        os.remove('temp_bad_server_config.yaml')

    def test_parse_settings_invalid_dict_structure(self):
        with open('temp_bad_server_config.yaml', 'w') as f:
            f.write('NOT YAML FORMAT.')

        with self.assertRaises(InvalidYamlError):
            parse_settings('temp_bad_server_config.yaml')
        os.remove('temp_bad_server_config.yaml')

    def test_no_server_config(self):
        with self.assertRaises(FileNotFoundError):
            parse_settings('temp_bad_server_config.yaml')

# Copyright Formic Technologies 2023
from yaml.scanner import ScannerError


class InvalidYamlError(ScannerError, RuntimeWarning):
    pass


class InvalidClientArgsError(Exception):
    pass

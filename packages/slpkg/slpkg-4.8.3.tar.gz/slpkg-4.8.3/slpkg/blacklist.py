#!/usr/bin/python3
# -*- coding: utf-8 -*-

import tomli
from pathlib import Path

from slpkg.configs import Configs
from slpkg.toml_error_message import TomlErrors
from slpkg.models.models import session as Session


class Blacklist(Configs):
    """ Reads and returns the blacklist. """

    def __init__(self):
        super(Configs, self).__init__()
        self.session = Session

        self.errors = TomlErrors()
        self.blacklist_file_toml = Path(self.etc_path, 'blacklist.toml')

    def packages(self) -> list:
        """ Reads the blacklist file. """
        if self.blacklist_file_toml.is_file():
            try:
                with open(self.blacklist_file_toml, 'rb') as black:
                    return tomli.load(black)['BLACKLIST']['PACKAGES']
            except (tomli.TOMLDecodeError, KeyError) as error:
                self.errors.raise_toml_error_message(error, self.blacklist_file_toml)

        return []

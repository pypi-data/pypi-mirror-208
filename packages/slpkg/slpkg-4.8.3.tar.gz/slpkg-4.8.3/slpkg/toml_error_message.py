#!/usr/bin/python3
# -*- coding: utf-8 -*-


class TomlErrors:

    def __init__(self):
        self.tool_name: str = 'slpkg'

    def raise_toml_error_message(self, error, toml_file) -> None:
        """ A general error message for .toml configs files. """
        raise SystemExit(f"\n{self.tool_name}: Error: {error}: in the configuration\n"
                         f"file '{toml_file}', edit the file and check for errors,\n"
                         f"or if you have upgraded the '{self.tool_name}' maybe you need to run:\n"
                         f"\n   $ slpkg_new-configs\n")

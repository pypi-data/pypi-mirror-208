#!/usr/bin/python3
# -*- coding: utf-8 -*-

from slpkg.configs import Configs


class Errors(Configs):

    def __init__(self):
        super(Configs, self).__init__()

    def raise_error_message(self, message: str, exit_status: int) -> None:
        """ A general method to raise an error message and exit. """
        print(f"\n{self.prog_name}: {self.bred}Error{self.endc}: {message}\n")
        raise SystemExit(exit_status)

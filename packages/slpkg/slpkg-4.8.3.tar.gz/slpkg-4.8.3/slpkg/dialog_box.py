#!/usr/bin/python3
# -*- coding: utf-8 -*-

import locale
from dialog import Dialog
from pathlib import Path
from typing import Union, Tuple

from slpkg.configs import Configs
from slpkg.views.version import Version

locale.setlocale(locale.LC_ALL, '')


class DialogBox(Configs):
    """ Class for dialog box"""

    def __init__(self):
        super(Configs).__init__()

        self.d = Dialog(dialog="dialog")
        self.d.set_background_title(f'{self.prog_name} {Version().version} - Software Package Manager')

    def checklist(self, text: str, packages: list, title: str, height: int, width: int,
                  list_height: int, choices: list) -> Tuple[bool, list]:
        """ Display a checklist box. """
        more_kwargs: dict = {}

        if self.dialog:
            more_kwargs.update({"item_help": True})

            code, tags = self.d.checklist(text=text, choices=choices, title=title, height=height,  width=width,
                                          list_height=list_height, help_status=True, **more_kwargs)

        else:
            code: bool = False
            tags: list = packages

        return code, tags

    def mixedform(self, text: str, title: str, elements: list, height: int, width: int) -> Tuple[bool, list]:
        """ Display a mixedform box. """
        more_kwargs: dict = {}

        if self.dialog:
            more_kwargs.update({"item_help": True,
                                "help_tags": True})
            code, tags = self.d.mixedform(text=text, title=title, elements=elements,  # type: ignore
                                          height=height, width=width, help_button=True,
                                          help_status=True, **more_kwargs)
        else:
            code: bool = False
            tags: list = elements

        return code, tags

    def msgbox(self, text: str, height: int, width: int) -> None:
        """ Display a message box. """
        if self.dialog:
            self.d.msgbox(text, height, width)

    def textbox(self, text: Union[str, Path], height: int, width: int) -> None:
        """ Display a text box. """
        if self.dialog:
            self.d.textbox(text, height, width)

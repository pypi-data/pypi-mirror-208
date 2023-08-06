#!/usr/bin/python3
# -*- coding: utf-8 -*-

import time
from progress.spinner import (PixelSpinner, LineSpinner,
                              MoonSpinner, PieSpinner, Spinner)

from slpkg.configs import Configs


class ProgressBar(Configs):

    def __init__(self):
        super(Configs, self).__init__()
        self.spinner = PixelSpinner
        self.color: str = self.endc
        self.spinners: dict = {}
        self.spinners_color: dict = {}

    def progress_bar(self, message: str, filename: str) -> None:
        """ Creating progress bar. """
        self.assign_spinners()
        self.assign_spinner_colors()
        self.set_spinner()
        self.set_color()

        if self.spinning_bar:
            bar_spinner = self.spinner(f'{self.endc}{message} {filename} {self.color}')
            # print('\033[F', end='', flush=True)
            try:
                while True:
                    time.sleep(0.1)
                    bar_spinner.next()
            except KeyboardInterrupt:
                raise SystemExit(1)
        else:
            print(f'{message} ', end='', flush=True)

    def assign_spinners(self) -> None:
        self.spinners: dict[str] = {
            'pixel': PixelSpinner,
            'line': LineSpinner,
            'moon': MoonSpinner,
            'pie': PieSpinner,
            'spinner': Spinner
        }

    def assign_spinner_colors(self) -> None:
        self.spinners_color: dict[str] = {
            'green': self.green,
            'violet': self.violet,
            'yellow': self.yellow,
            'blue': self.blue,
            'cyan': self.cyan,
            'grey': self.grey,
            'red': self.red,
            '': self.endc
        }

    def set_spinner(self) -> None:
        try:
            self.spinner = self.spinners[self.progress_spinner]
        except KeyError:
            self.spinner = PixelSpinner

    def set_color(self) -> None:
        try:
            self.color: str = self.spinners_color[self.spinner_color]
        except KeyError:
            self.color: str = self.endc

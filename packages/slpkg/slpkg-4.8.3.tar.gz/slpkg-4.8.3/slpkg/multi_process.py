#!/usr/bin/python3
# -*- coding: utf-8 -*-

import subprocess
from multiprocessing import Process

from slpkg.configs import Configs
from slpkg.utilities import Utilities
from slpkg.progress_bar import ProgressBar


class MultiProcess(Configs):

    def __init__(self, flags: list):
        super(Configs, self).__init__()

        self.utils = Utilities()
        self.progress = ProgressBar()

        self.stderr = None
        self.stdout = None

        self.option_for_no_silent: bool = self.utils.is_option(
            ['-n', '--no-silent'], flags)

    def process(self, command: str, filename: str, process_message: str, progress_message: str) -> None:
        """ Starting multiprocessing install/upgrade process. """
        if self.silent_mode and not self.option_for_no_silent:
            done: str = f"{'':>1}{self.byellow}Done{self.endc}"
            self.stderr = subprocess.DEVNULL
            self.stdout = subprocess.DEVNULL

            # Starting multiprocessing
            p1 = Process(target=self.utils.process, args=(command, self.stderr, self.stdout))
            p2 = Process(target=self.progress.progress_bar, args=(f'{progress_message}:', filename))

            p1.start()
            p2.start()

            # Wait until process 1 finish
            p1.join()

            # Terminate process 2 if process 1 finished
            if not p1.is_alive():
                if p1.exitcode != 0:
                    done: str = f'{self.bred}Failed: {self.endc}{process_message}.'

                print(f'{self.endc}{done}', end='')
                p2.terminate()

            # Wait until process 2 finish
            p2.join()

            # Restore the terminal cursor
            print('\x1b[?25h', self.endc)
        else:
            self.utils.process(command, self.stderr, self.stdout)

#!/usr/bin/python3
# -*- coding: utf-8 -*-

import shutil

from slpkg.configs import Configs


class AsciiBox(Configs):

    def __init__(self):
        super(Configs, self).__init__()
        self.columns, self.rows = shutil.get_terminal_size()
        self.package_alignment: int = self.columns - 61
        self.version_alignment: int = 29
        self.size_alignment: int = 14
        self.repo_alignment: int = 14

        if self.package_alignment < 1:
            self.package_alignment = 1

        self.vertical_line: str = '|'
        self.horizontal_line: str = '='
        self.horizontal_vertical: str = '+'
        self.upper_right_corner: str = '+'
        self.lower_left_corner: str = '+'
        self.lower_right_corner: str = '+'
        self.upper_left_corner: str = '+'
        self.horizontal_and_up: str = '+'
        self.horizontal_and_down: str = '+'
        self.vertical_and_right: str = '+'
        self.vertical_and_left: str = '+'

        if self.ascii_characters:
            self.vertical_line: str = '│'
            self.horizontal_line: str = '─'
            self.horizontal_vertical: str = '┼'
            self.upper_right_corner: str = '┐'
            self.lower_left_corner: str = '└'
            self.lower_right_corner: str = '┘'
            self.upper_left_corner: str = '┌'
            self.horizontal_and_up: str = '┴'
            self.horizontal_and_down: str = '┬'
            self.vertical_and_right: str = '├'
            self.vertical_and_left: str = '┤'

    def draw_package_title(self, message: str, title: str) -> None:
        title = title.title()
        print(f"{self.bgreen}{self.upper_left_corner}{self.horizontal_line * (self.columns - 2)}"
              f"{self.upper_right_corner}")
        print(f"{self.vertical_line}{title.center(self.columns - 2, ' ')}{self.vertical_line}")
        self.draw_middle_line()
        print(f"{self.vertical_line} {self.endc}{message.ljust(self.columns - 3, ' ')}"
              f"{self.bgreen}{self.vertical_line}")
        self.draw_middle_line()
        print(f"{self.bgreen}{self.vertical_line}{self.endc} {'Package:':<{self.package_alignment}}"
              f"{'Version:':<{self.version_alignment}}{'Size:':<{self.size_alignment}}{'Repo:':>{self.repo_alignment}} "
              f"{self.bgreen}{self.vertical_line}{self.endc}")

    def draw_package_line(self, package: str, version: str, size: str, color: str, repo: str) -> None:
        if len(version) >= 20 and self.columns <= 80:
            version: str = f'{version[:self.version_alignment - 5]}...'
        if len(package) >= 15 and self.columns <= 80:
            package: str = f'{package[:self.package_alignment - 5]}...'
        print(f"{self.bgreen}{self.vertical_line} {self.bold}{color}{package:<{self.package_alignment}}{self.endc}"
              f"{self.bgreen}{version:<{self.version_alignment}}{self.endc}{size:<{self.size_alignment}}{self.blue}"
              f"{repo:>{self.repo_alignment}}{self.bgreen} {self.vertical_line}{self.endc}")

    def draw_middle_line(self) -> None:
        print(f"{self.bgreen}{self.vertical_and_right}{self.horizontal_line * (self.columns - 2)}"
              f"{self.vertical_and_left}")

    def draw_dependency_line(self) -> None:
        print(f"{self.bgreen}{self.vertical_line}{self.endc} Dependencies:{' ' * (self.columns - 16)}"
              f"{self.bgreen}{self.vertical_line}{self.endc}")

    def draw_bottom_line(self) -> None:
        print(f"{self.bold}{self.green}{self.lower_left_corner}{self.horizontal_line * (self.columns - 2)}"
              f"{self.lower_right_corner}{self.endc}")

    def draw_checksum_error_box(self, name: str, checksum: str, file_check: str) -> None:
        print(f"{self.bred}{self.upper_left_corner}{self.horizontal_line * (self.columns - 2)}"
              f"{self.upper_right_corner}")
        print(f"{self.bred}{self.vertical_line}{self.bred} FAILED:{self.endc} MD5SUM check for "
              f"'{self.cyan}{name}'{' ' * (self.columns - len(name) - 30)}{self.red}{self.vertical_line}")
        print(f"{self.bred}{self.vertical_and_right}{self.horizontal_line * (self.columns - 2)}"
              f"{self.vertical_and_left}")
        print(f"{self.bred}{self.vertical_line}{self.yellow} Expected:{self.endc} {checksum}{self.bred}"
              f"{' ' * (self.columns - (len(checksum)) - 13)}{self.vertical_line}")
        print(f"{self.bred}{self.vertical_line}{self.violet} Found:{self.endc} {file_check}{self.bred}"
              f"{' ' * (self.columns - (len(file_check)) - 10)}{self.vertical_line}")
        print(f"{self.bred}{self.lower_left_corner}{self.horizontal_line * (self.columns - 2)}"
              f"{self.lower_right_corner}{self.endc}")

    def draw_log_package(self, package: str) -> None:
        print(f"{'':>2}{self.lower_left_corner}{self.horizontal_line}{self.cyan} {package}{self.endc}\n")

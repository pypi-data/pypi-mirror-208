#!/usr/bin/python3
# -*- coding: utf-8 -*-

import sys
import shutil
import difflib
import subprocess
from typing import Any
from pathlib import Path


class NewConfigs:

    def __init__(self, options: list):
        self.options: list = options
        self.etc_path: Path = Path('/etc/slpkg')
        self.slpkg_config: Path = Path(self.etc_path, 'slpkg.toml')
        self.repositories_config: Path = Path(self.etc_path, 'repositories.toml')
        self.blacklist_config: Path = Path(self.etc_path, 'blacklist.toml')
        self.slpkg_config_new: Path = Path(self.etc_path, 'slpkg.toml.new')
        self.repositories_config_new: Path = Path(self.etc_path, 'repositories.toml.new')
        self.blacklist_config_new: Path = Path(self.etc_path, 'blacklist.toml.new')

        self.bold: str = '\033[1m'
        self.red: str = '\x1b[91m'
        self.bred: str = f'{self.bold}{self.red}'
        self.green: str = '\x1b[32m'
        self.bgreen: str = f'{self.bold}{self.green}'
        self.yellow: str = '\x1b[93m'
        self.byellow: str = f'{self.bold}{self.yellow}'
        self.cyan: str = '\x1b[96m'
        self.blue: str = '\x1b[94m'
        self.grey: str = '\x1b[38;5;247m'
        self.violet: str = '\x1b[35m'
        self.endc: str = '\x1b[0m'

        self.set_no_colors()

        self.choice = None

    def set_no_colors(self) -> None:
        if '--no-colors' in self.options:
            self.bold: str = str()
            self.red: str = str()
            self.bred: str = str()
            self.green: str = str()
            self.bgreen: str = str()
            self.yellow: str = str()
            self.byellow: str = str()
            self.cyan: str = str()
            self.blue: str = str()
            self.grey: str = str()
            self.violet: str = str()
            self.endc: str = str()

    def check(self) -> None:
        """ Checks for .new files. """
        print('\nChecking for NEW configuration files...')
        if (self.slpkg_config_new.is_file() or self.blacklist_config_new.is_file()
                or self.repositories_config_new.is_file()):
            print('\nThere are NEW files:\n')

            if self.slpkg_config_new.is_file():
                print(f"{self.bgreen:>12}{self.slpkg_config_new}{self.endc}")

            if self.repositories_config_new.is_file():
                print(f"{self.bgreen:>12}{self.repositories_config_new}{self.endc}")

            if self.blacklist_config_new.is_file():
                print(f"{self.bgreen:>12}{self.blacklist_config_new}{self.endc}")

            print(f'\nWhat would you like to do ({self.byellow}K{self.endc}/{self.byellow}O{self.endc}/'
                  f'{self.byellow}R{self.endc}/{self.byellow}P{self.endc})?\n')

            print(f"{'':>2}({self.byellow}K{self.endc})eep the old files and consider '.new' files later.\n"
                  f"{'':>2}({self.byellow}O{self.endc})verwrite all old files with the new ones.\n"
                  f"{'':>5}The old files will be stored with the suffix '.orig'.\n"
                  f"{'':>2}({self.byellow}R{self.endc})emove all '.new' files.\n"
                  f"{'':>2}({self.byellow}P{self.endc})rompt K, O, R, D, V selection for every single file.\n")

            self.menu()

        elif (not self.slpkg_config_new.is_file() and not self.blacklist_config_new.is_file()
              and not self.repositories_config_new.is_file()):
            print(f"\n{'No .new files found.':>23}\n")

    def menu(self) -> None:
        """ Menu of choices. """
        choice: str = input('Choice: ')

        choice: str = choice.lower()

        arguments: dict[str] = {
            'k': self.keep,
            'o': self.overwrite,
            'r': self.remove,
            'p': self.prompt
        }

        try:
            arguments[choice]()
        except KeyError:
            self.keep()

    @staticmethod
    def keep() -> None:
        print("\nNo changes were made.\n")

    def overwrite(self) -> None:
        """ Copy tne .new files and rename the olds to .orig.  """
        if self.slpkg_config_new.is_file():
            self.overwrite_config_file()

        if self.repositories_config_new.is_file():
            self.overwrite_repositories_file()

        if self.blacklist_config_new.is_file():
            self.overwrite_blacklist_file()
        print()  # new line

    def overwrite_config_file(self) -> None:
        """ Copy tne slpkg.toml.new file and rename the old to .orig. """
        if self.slpkg_config.is_file():
            shutil.copy(self.slpkg_config, f"{self.slpkg_config}.orig")
            print(f"\ncp {self.green}{self.slpkg_config}{self.endc} -> {self.slpkg_config}.orig")

        shutil.move(self.slpkg_config_new, self.slpkg_config)
        print(f"mv {self.slpkg_config_new} -> {self.green}{self.slpkg_config}{self.endc}")

    def overwrite_repositories_file(self) -> None:
        """ Copy tne repositories.toml.new file and rename the old to .orig. """
        if self.slpkg_config.is_file():
            shutil.copy(self.repositories_config, f"{self.repositories_config}.orig")
            print(f"\ncp {self.green}{self.repositories_config}{self.endc} -> {self.repositories_config}.orig")

        shutil.move(self.repositories_config_new, self.repositories_config)
        print(f"mv {self.repositories_config_new} -> {self.green}{self.repositories_config}{self.endc}")

    def overwrite_blacklist_file(self) -> None:
        """ Copy tne blacklist.toml.new file and rename the old to .orig. """
        if self.blacklist_config.is_file():
            shutil.copy(self.blacklist_config, f"{self.blacklist_config}.orig")
            print(f"\ncp {self.green}{self.blacklist_config}{self.endc} -> {self.blacklist_config}.orig")

        shutil.move(self.blacklist_config_new, self.blacklist_config)
        print(f"mv {self.blacklist_config_new} -> {self.green}{self.blacklist_config}{self.endc}")

    def remove(self) -> None:
        """ Removes the .new files. """
        print()  # new line
        self.remove_config_new_file()
        self.remove_repositories_new_file()
        self.remove_blacklist_new_file()
        print()  # new line

    def remove_config_new_file(self) -> None:
        """ Remove slpkg.toml.new file. """
        if self.slpkg_config_new.is_file():
            self.slpkg_config_new.unlink()
            print(f"rm {self.red}{self.slpkg_config_new}{self.endc}")

    def remove_repositories_new_file(self) -> None:
        """ Remove repositories.toml.new file. """
        if self.repositories_config_new.is_file():
            self.repositories_config_new.unlink()
            print(f"rm {self.red}{self.repositories_config_new}{self.endc}")

    def remove_blacklist_new_file(self) -> None:
        """ Remove blacklist.toml.new file. """
        if self.blacklist_config_new.is_file():
            self.blacklist_config_new.unlink()
            print(f"rm {self.red}{self.blacklist_config_new}{self.endc}")

    def prompt(self) -> None:
        """ Prompt K, O, R selection for every single file. """
        print(f"\n{'':>2}({self.byellow}K{self.endc})eep, ({self.byellow}O{self.endc})verwrite, "
              f"({self.byellow}R{self.endc})emove, ({self.byellow}D{self.endc})iff, "
              f"({self.byellow}V{self.endc})imdiff\n")

        if self.slpkg_config_new.is_file():
            self.prompt_slpkg_config()

        if self.repositories_config_new.is_file():
            self.prompt_repositories_config()

        if self.blacklist_config_new.is_file():
            self.prompt_blacklist_config()

    def prompt_slpkg_config(self):
        make: str = input(f'{self.bgreen}{self.slpkg_config_new}{self.endc} - '
                          f'({self.byellow}K{self.endc}/{self.byellow}O{self.endc}/'
                          f'{self.byellow}R{self.endc}/{self.byellow}D{self.endc}/'
                          f'{self.byellow}V{self.endc}): ')

        if make.lower() == 'k':
            pass
        if make.lower() == 'o':
            self.overwrite_config_file()
            print()  # new line
        if make.lower() == 'r':
            print()  # new line
            self.remove_config_new_file()
            print()  # new line
        if make.lower() == 'd':
            self.diff_files(self.slpkg_config_new, self.slpkg_config)
        if make.lower() == 'v':
            self.vimdiff(self.slpkg_config_new, self.slpkg_config)

    def prompt_repositories_config(self):
        make: str = input(f'{self.bgreen}{self.repositories_config_new}{self.endc} - '
                          f'({self.byellow}K{self.endc}/{self.byellow}O{self.endc}/'
                          f'{self.byellow}R{self.endc}/{self.byellow}D{self.endc}/'
                          f'{self.byellow}V{self.endc}): ')

        if make.lower() == 'k':
            pass
        if make.lower() == 'o':
            self.overwrite_repositories_file()
            print()  # new line
        if make.lower() == 'r':
            print()  # new line
            self.remove_repositories_new_file()
            print()  # new line
        if make.lower() == 'd':
            self.diff_files(self.repositories_config_new, self.repositories_config)
        if make.lower() == 'v':
            self.vimdiff(self.repositories_config_new, self.repositories_config)

    def prompt_blacklist_config(self):
        make: str = input(f'{self.bgreen}{self.blacklist_config_new}{self.endc} - '
                          f'({self.byellow}K{self.endc}/{self.byellow}O{self.endc}/'
                          f'{self.byellow}R{self.endc}/{self.byellow}D{self.endc}/'
                          f'{self.byellow}V{self.endc}): ')

        if make.lower() == 'k':
            pass
        if make.lower() == 'o':
            self.overwrite_blacklist_file()
            print()  # new line
        if make.lower() == 'r':
            print()  # new line
            self.remove_blacklist_new_file()
            print()  # new line
        if make.lower() == 'd':
            self.diff_files(self.blacklist_config_new, self.blacklist_config)
        if make.lower() == 'v':
            self.vimdiff(self.blacklist_config_new, self.blacklist_config)

    @staticmethod
    def diff_files(file2: Any, file1: Any) -> None:
        """ Diff the .new and the current file. """
        with open(file1, 'r') as f1:
            with open(file2, 'r') as f2:
                diff = difflib.context_diff(
                    f1.readlines(),
                    f2.readlines(),
                    fromfile=str(file1),
                    tofile=str(file2)
                )
                for line in diff:
                    print(line, end='')

    @staticmethod
    def vimdiff(file1: Any, file2: Any) -> None:
        output = subprocess.call(f'vimdiff {file1} {file2}', shell=True)
        if output != 0:
            raise SystemExit(output)


def main() -> None:
    args: list = sys.argv
    args.pop(0)

    options: list = [
        '--no-colors',
        '-h',
        '--help'
    ]

    if len(args) == 1:
        if options[1] in args or options[2] in args:
            print('slpkg_new-configs [OPTIONS]\n'
                  '\n  --no-colors     Disable the output colors.\n'
                  '  -h, --help      Show this message and exit.\n')
            sys.exit()
        elif args[0] == options[0]:
            pass
        else:
            print('\ntry: slpkg_new-configs --help\n')
            sys.exit(1)
    elif len(args) > 1:
        print('\ntry: slpkg_new-configs --help\n')
        sys.exit(1)

    try:
        config = NewConfigs(args)
        config.check()
    except KeyboardInterrupt:
        raise SystemExit()

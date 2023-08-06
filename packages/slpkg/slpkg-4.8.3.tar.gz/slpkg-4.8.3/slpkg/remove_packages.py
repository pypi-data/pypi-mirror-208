#!/usr/bin/python3
# -*- coding: utf-8 -*-

import os
import time

from slpkg.configs import Configs
from slpkg.utilities import Utilities
from slpkg.dialog_box import DialogBox
from slpkg.views.views import ViewMessage
from slpkg.multi_process import MultiProcess
from slpkg.models.models import LogsDependencies
from slpkg.models.models import session as Session


class RemovePackages(Configs):
    """ Removes installed packages with dependencies if they installed with
        slpkg install command.
    """

    def __init__(self, packages: list, flags: list):
        super(Configs, self).__init__()
        self.packages: list = packages
        self.flags: list = flags

        self.session = Session
        self.dialogbox = DialogBox()
        self.utils = Utilities()
        self.multi_proc = MultiProcess(flags)
        self.view = ViewMessage(flags)

        self.logs_dependencies: dict = {}
        self.installed_packages: list = []
        self.installed_dependencies: list = []
        self.dependencies: list = []

        self.option_for_resolve_off: bool = self.utils.is_option(
            ['-O', '--resolve-off'], flags)

        self.option_for_yes: bool = self.utils.is_option(
            ['-y', '--yes'], flags)

    def remove(self) -> None:
        self.query_logs_dependencies()
        self.save_dependencies_for_remove()
        self.remove_doubles_dependencies()
        self.remove_doubles_installed_dependencies()
        self.add_dependencies_to_remove()
        self.choose_dependencies_for_remove()
        self.save_packages_for_remove()

        self.view.remove_packages(self.packages, self.dependencies)
        self.view.question()

        start: float = time.time()
        self.remove_packages()
        elapsed_time: float = time.time() - start
        self.utils.finished_time(elapsed_time)

    def save_dependencies_for_remove(self) -> None:
        if not self.option_for_resolve_off:
            for package in self.packages:
                if self.logs_dependencies.get(package):
                    requires: tuple = self.logs_dependencies[package]

                    for require in requires:
                        installed: str = self.utils.is_package_installed(require)
                        if installed and require not in self.packages:
                            self.dependencies.append(require)
                            self.installed_dependencies.append(installed)

    def remove_doubles_dependencies(self) -> None:
        self.dependencies: list = list(set(self.dependencies))

    def remove_doubles_installed_dependencies(self):
        self.installed_dependencies: list = list(set(self.installed_dependencies))

    def add_dependencies_to_remove(self) -> None:
        self.installed_packages.extend(self.installed_dependencies)

    def save_packages_for_remove(self) -> None:
        for package in self.packages:
            installed: str = self.utils.is_package_installed(package)
            if installed:
                self.installed_packages.append(installed)

    def remove_packages(self) -> None:
        for package in self.installed_packages:
            command: str = f'{self.removepkg} {package}'
            name: str = self.utils.split_package(package)['name']
            process_message: str = f"package '{name}' to remove"
            progress_message: str = f'{self.bold}{self.red}Remove{self.endc}'

            dependencies: list = self.is_dependency(name)
            if dependencies:
                self.view_warning_message(dependencies, name)
                if not self.question_to_remove():
                    continue

            self.multi_proc.process(command, package, process_message, progress_message)
            self.delete_package_from_logs(name)

    def is_dependency(self, name: str) -> list:
        dependencies: list = []
        for package, requires in self.logs_dependencies.items():
            if name in requires and package not in self.packages:
                dependencies.append(package)

        if dependencies:
            return dependencies

    def question_to_remove(self) -> bool:
        if not self.option_for_yes and self.ask_question:
            answer: str = input('\nDo you want to remove? [y/N] ')
            if answer in ['Y', 'y']:
                return True
            print()

    def view_warning_message(self, dependencies: list, name: str) -> None:
        print(f"\n{self.bold}{self.violet}WARNING!{self.endc}: The package '{self.red}{name}{self.endc}' "
              f"is a dependency for the packages:")
        for dependency in dependencies:
            print(f"{self.cyan:>16}-> {dependency}{self.endc}")

    def query_logs_dependencies(self) -> None:
        package_requires: tuple = self.session.query(
            LogsDependencies.name, LogsDependencies.requires).all()
        for package in package_requires:
            self.logs_dependencies[package[0]] = package[1].split()

    def delete_package_from_logs(self, package) -> None:
        if not self.option_for_resolve_off:
            self.session.query(LogsDependencies).filter(
                LogsDependencies.name == package).delete()
            self.session.commit()

    def choose_dependencies_for_remove(self) -> None:
        height: int = 10
        width: int = 70
        list_height: int = 0
        choices: list = []
        title: str = " Choose dependencies you want to remove "

        for package in self.dependencies:
            installed_package: str = self.utils.is_package_installed(package)
            installed_version: str = self.utils.split_package(installed_package)['version']
            choices.extend([(package, installed_version, True, f'Package: {installed_package}')])

        text: str = f'There are {len(choices)} dependencies:'
        code, self.dependencies = self.dialogbox.checklist(text, self.dependencies, title, height,
                                                           width, list_height, choices)
        os.system('clear')

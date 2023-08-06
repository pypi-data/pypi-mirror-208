#!/usr/bin/python3
# -*- coding: utf-8 -*-

import logging
from typing import Generator
from packaging.version import parse, InvalidVersion

from slpkg.configs import Configs
from slpkg.utilities import Utilities
from slpkg.repositories import Repositories
from slpkg.logging_config import LoggingConfig


class Upgrade(Configs):
    """ Upgrade the installed packages. """

    def __init__(self, repository: str, data: dict):
        super(Configs, self).__init__()
        self.repository: str = repository
        self.data: dict = data

        self.utils = Utilities()
        self.repos = Repositories()

        self.is_binary: bool = self.utils.is_binary_repo(repository)

        logging.basicConfig(filename=LoggingConfig.log_file,
                            filemode=LoggingConfig.filemode,
                            encoding=LoggingConfig.encoding,
                            level=LoggingConfig.level)

    def packages(self) -> Generator:
        """ Returns the upgradable packages. """

        # Returns the matched packages between two lists.
        matched_packages: tuple = tuple(set(self.utils.installed_packages.keys()) & set(self.data.keys()))

        for package in matched_packages:
            if self.is_package_upgradeable(package):
                yield package

    def is_package_upgradeable(self, name: str) -> bool:
        """ Compares version of packages and returns the maximum. """
        repo_package_version = repo_package_build = '0'
        inst_package_version = inst_package_build = '0'
        inst_package: str = self.utils.is_package_installed(name)

        if inst_package and inst_package.endswith(self.repos.repositories[self.repository]['repo_tag']):
            inst_package_version: str = self.utils.split_package(inst_package)['version']
            inst_package_build: str = self.utils.split_package(inst_package)['build']
            repo_package_version: str = self.data[name]['version']

            if self.is_binary and self.data.get(name):
                repo_package: str = self.data[name]['package']
                repo_package_build: str = self.utils.split_package(repo_package)['build']
            else:
                repo_location: str = self.data[name]['location']
                repo_package_build: str = self.utils.read_slackbuild_build_tag(
                    name, repo_location, self.repository)

        repository_package: str = f'{name}-{repo_package_version}'
        installed_package: str = f'{name}-{inst_package_version}'

        try:
            if parse(repository_package) > parse(installed_package):
                return True

            if (parse(repository_package) == parse(installed_package)
                    and parse(repo_package_build) > parse(inst_package_build)):
                return True

        except InvalidVersion:
            logger = logging.getLogger(LoggingConfig.date_time)
            logger.exception(f"{self.__class__.__name__}: "
                             f"{self.__class__.is_package_upgradeable.__name__}: "
                             f"{self.repos.repositories[self.repository]['repo_tag']}, "
                             f"{repository_package=}, {installed_package=}, {repository_package > installed_package}, "
                             f"{repository_package == installed_package and repo_package_build > inst_package_build}")

            if repository_package > installed_package:
                return True

            if repository_package == installed_package and repo_package_build > inst_package_build:
                return True

        return False

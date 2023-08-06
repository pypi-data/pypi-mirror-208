#!/usr/bin/python3
# -*- coding: utf-8 -*-

from slpkg.configs import Configs
from slpkg.utilities import Utilities
from slpkg.sbos.queries import SBoQueries
from slpkg.repositories import Repositories
from slpkg.binaries.queries import BinQueries


class SearchPackage(Configs):
    """ Search packages from the repositories. """

    def __init__(self, data: dict, packages: list, repository: str):
        super(Configs, self).__init__()
        self.data: dict = data
        self.packages: list = packages
        self.repository: str = repository

        self.utils = Utilities()
        self.repos = Repositories()

        self.matching: int = 0
        self.data_dict: dict = {}

        self.is_binary: bool = self.utils.is_binary_repo(repository)

    def search(self) -> None:
        print(f'The list below shows the repo '
              f'packages that contains \'{", ".join([p for p in self.packages])}\':\n')

        if self.repository == '*':
            self.search_to_all_repositories()
        else:
            self.search_to_the_repository()

        self.summary_of_searching()

    def search_to_all_repositories(self) -> None:
        for repo, item in self.repos.repositories.items():
            if item['enable']:  # Check if the repository is enabled
                if self.utils.is_binary_repo(repo):
                    data: dict = BinQueries(repo).repository_data()
                else:
                    data: dict = SBoQueries(repo).repository_data()
                self.search_for_the_packages(data, repo)

    def search_to_the_repository(self) -> None:
        if self.is_binary:
            data: dict = BinQueries(self.repository).repository_data()
        else:
            data: dict = SBoQueries(self.repository).repository_data()
        self.search_for_the_packages(data, self.repository)

    def search_for_the_packages(self, data: dict, repo: str) -> None:
        for package in self.packages:
            for name, data_pkg in data.items():

                if package in name or package == '*':
                    self.matching += 1

                    self.data_dict[self.matching] = {
                        'repository': repo,
                        'name': name,
                        'version': data_pkg['version']
                    }

    def summary_of_searching(self) -> None:
        if self.matching:
            for item in self.data_dict.values():
                print(f"{item['repository']}: {self.cyan}{item['name']}{self.endc} "
                      f"{self.yellow}{item['version']}{self.endc}")

            print(f'\n{self.grey}Total found {self.matching} packages.{self.endc}')
        else:
            print('\nDoes not match any package.\n')

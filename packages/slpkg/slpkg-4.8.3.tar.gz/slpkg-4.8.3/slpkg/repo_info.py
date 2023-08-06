#!/usr/bin/python3
# -*- coding: utf-8 -*-

import shutil

from slpkg.configs import Configs
from slpkg.utilities import Utilities
from slpkg.repositories import Repositories
from slpkg.models.models import session as Session
from slpkg.models.models import (LastRepoUpdated, SBoTable,
                                 PonceTable, BinariesTable)


class RepoInfo(Configs):

    def __init__(self, flags: list, repository: str):
        super(Configs, self).__init__()
        self.flags: list = flags
        self.repository: str = repository

        self.session = Session
        self.utils = Utilities()
        self.repos = Repositories()
        self.columns, self.rows = shutil.get_terminal_size()
        self.name_alignment: int = self.columns - 62

        if self.name_alignment < 1:
            self.name_alignment: int = 1

        self.enabled: int = 0
        self.total_packages: int = 0

        self.option_for_repository: bool = self.utils.is_option(
            ['-o', '--repository='], flags)

    def info(self) -> None:
        """ Prints information about repositories. """
        self.view_the_title()

        if self.option_for_repository:
            self.view_the_repository_information()
        else:
            self.view_the_repositories_information()

    def count_the_packages(self, repository: str) -> int:
        sbo_table: dict = {
            self.repos.sbo_repo_name: SBoTable,
            self.repos.ponce_repo_name: PonceTable
        }
        if self.utils.is_binary_repo(repository):
            count = self.session.query(BinariesTable).where(
                BinariesTable.repo == repository).count()
        else:
            count = self.session.query(sbo_table[repository].id).count()

        self.total_packages += count

        return count

    def last_repository_updated(self, repository: str) -> str:
        date: str = self.session.query(
            LastRepoUpdated.date).where(
            LastRepoUpdated.repo == repository).first()

        if date[0] is None:
            date: tuple = ('',)

        return date[0]

    def view_the_title(self) -> None:
        title: str = f'repositories information:'.title()
        if self.option_for_repository:
            title: str = f'repository information:'.title()
        print(title)
        print('=' * self.columns)
        print(f"{'Name:':<{self.name_alignment}}{'Status:':<15}{'Last Updated:':<35}{'Packages:':>12}")
        print('=' * self.columns)

    def view_the_repository_information(self) -> None:
        count: int = 0
        color: str = self.red
        status: str = 'Disabled'
        date: str = self.last_repository_updated(self.repository)

        if self.repos.repositories[self.repository]['enable']:
            status: str = 'Enabled'
            color: str = self.green
            count: int = self.count_the_packages(self.repository)

        self.view_the_line_information(self.repository, status, date, count, color)
        self.view_summary_of_repository()

    def view_the_repositories_information(self) -> None:
        for repo, item in self.repos.repositories.items():
            count: int = 0
            color: str = self.red
            status: str = 'Disabled'
            date: str = self.last_repository_updated(repo)

            if item['enable']:
                self.enabled += 1
                status: str = 'Enabled'
                color: str = self.green
                count: int = self.count_the_packages(repo)

            self.view_the_line_information(repo, status, date, count, color)
        self.view_summary_of_all_repositories()

    def view_the_line_information(self, repository: str, status: str, date: str, count: int, color: str) -> None:
        print(f"{self.cyan}{repository:<{self.name_alignment}}{self.endc}{color}{status:<15}{self.endc}{date:<35}"
              f"{self.yellow}{count:>12}{self.endc}")

    def view_summary_of_repository(self) -> None:
        print('=' * self.columns)
        print(f"{self.grey}Total {self.total_packages} packages available from the '{self.repository}' repository.\n")

    def view_summary_of_all_repositories(self) -> None:
        print('=' * self.columns)
        print(f"{self.grey}Total of {self.enabled}/{len(self.repos.repositories)} "
              f"repositories are enabled with {self.total_packages} packages available.\n")

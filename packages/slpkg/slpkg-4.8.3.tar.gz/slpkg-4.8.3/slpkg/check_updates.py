#!/usr/bin/python3
# -*- coding: utf-8 -*-

import os
import logging
from pathlib import Path
from multiprocessing import Process
from urllib3 import PoolManager, ProxyManager, make_headers

from slpkg.configs import Configs
from slpkg.utilities import Utilities
from slpkg.progress_bar import ProgressBar
from slpkg.repositories import Repositories
from slpkg.logging_config import LoggingConfig


class CheckUpdates(Configs):
    """ Check for changes in the ChangeLog file. """

    def __init__(self, flags: list, repository: str):
        super(Configs, self).__init__()
        self.flags: list = flags
        self.repository: str = repository

        self.utils = Utilities()
        self.progress = ProgressBar()
        self.repos = Repositories()

        self.compare: dict = {}
        self.http = PoolManager()
        self.proxy_default_headers = make_headers(
            proxy_basic_auth=f'{self.proxy_username}:{self.proxy_password}')

        self.is_binary: bool = self.utils.is_binary_repo(repository)

        self.option_for_repository: bool = self.utils.is_option(
            ['-o', '--repository='], flags)

        logging.basicConfig(filename=LoggingConfig.log_file,
                            filemode=LoggingConfig.filemode,
                            encoding=LoggingConfig.encoding,
                            level=LoggingConfig.level)

    def check_the_repositories(self) -> dict:
        if self.option_for_repository:
            self.check_updates_for_repository()
        else:
            self.check_updates_for_repositories()

        return self.compare

    def check_updates_for_repository(self):
        sbo_repository: dict = {
            self.repos.sbo_repo_name: self.sbo_repository,
            self.repos.ponce_repo_name: self.ponce_repository
        }

        if self.is_binary:
            self.binary_repository(self.repository)
        else:
            sbo_repository[self.repository]()

    def check_updates_for_repositories(self):
        if self.repos.sbo_repo:
            self.sbo_repository()

        if self.repos.ponce_repo:
            self.ponce_repository()

        for repo in list(self.repos.repositories.keys())[2:]:
            if self.repos.repositories[repo]['enable']:
                self.binary_repository(repo)

    def binary_repository(self, repo: str) -> None:
        local_chg_txt: Path = Path(self.repos.repositories[repo]['path'],
                                   self.repos.repositories[repo]['changelog_txt'])
        repo_chg_txt: str = (f"{self.repos.repositories[repo]['mirror'][0]}"
                             f"{self.repos.repositories[repo]['changelog_txt']}")
        self.compare[repo] = self.compare_the_changelogs(local_chg_txt, repo_chg_txt)

    def sbo_repository(self) -> None:
        local_chg_txt: Path = Path(self.repos.sbo_repo_path, self.repos.sbo_repo_changelog)
        repo_chg_txt: str = f'{self.repos.sbo_repo_mirror[0]}{self.repos.sbo_repo_changelog}'
        self.compare[self.repos.sbo_repo_name] = self.compare_the_changelogs(local_chg_txt, repo_chg_txt)

    def ponce_repository(self) -> None:
        local_chg_txt: Path = Path(self.repos.ponce_repo_path, self.repos.ponce_repo_changelog)
        repo_chg_txt: str = f'{self.repos.ponce_repo_mirror[0]}{self.repos.ponce_repo_changelog}'
        self.compare[self.repos.ponce_repo_name] = self.compare_the_changelogs(local_chg_txt, repo_chg_txt)

    def compare_the_changelogs(self, local_chg_txt: Path, repo_chg_txt: str) -> bool:
        local_size: int = 0

        if self.proxy_address.startswith('http'):
            self.set_http_proxy_server()

        if self.proxy_address.startswith('socks'):
            self.set_socks_proxy_server()

        repo = self.http.request('GET', repo_chg_txt)
        if local_chg_txt.is_file():
            local_size: int = int(os.stat(local_chg_txt).st_size)

        repo_size: int = int(repo.headers['Content-Length'])

        logger = logging.getLogger(LoggingConfig.date_time)
        logger.info(f'{self.__class__.__name__}: '
                    f'{self.__class__.compare_the_changelogs.__name__}: '
                    f'{local_chg_txt=}, {local_size=}, '
                    f'{repo_chg_txt=}, {repo_size=}, '
                    f'{local_size != repo_size}')

        return local_size != repo_size

    def set_http_proxy_server(self):
        self.http = ProxyManager(f'{self.proxy_address}', headers=self.proxy_default_headers)

    def set_socks_proxy_server(self):
        try:  # Try to import PySocks if it's installed.
            from urllib3.contrib.socks import SOCKSProxyManager
        except (ModuleNotFoundError, ImportError) as error:
            print(error)
        # https://urllib3.readthedocs.io/en/stable/advanced-usage.html#socks-proxies
        self.http = SOCKSProxyManager(f'{self.proxy_address}', headers=self.proxy_default_headers)

    def check_for_updates(self) -> None:
        self.check_the_repositories()
        self.view_messages()

    def view_messages(self) -> None:
        print()
        for repo, comp in self.compare.items():
            if comp:
                print(f"\n{self.endc}There are new updates available for the "
                      f"'{self.bgreen}{repo}{self.endc}' repository!")

        if True not in self.compare.values():
            print(f'\n{self.endc}{self.yellow}No updated packages since the last check.{self.endc}')

    def updates(self) -> None:
        message: str = 'Checking for news, please wait...'

        # Starting multiprocessing
        p1 = Process(target=self.check_for_updates)
        p2 = Process(target=self.progress.progress_bar, args=(message, ''))

        p1.start()
        p2.start()

        # Wait until process 1 finish
        p1.join()

        # Terminate process 2 if process 1 finished
        if not p1.is_alive():
            p2.terminate()

        # Wait until process 2 finish
        p2.join()

        # Restore the terminal cursor
        print('\x1b[?25h', self.endc)

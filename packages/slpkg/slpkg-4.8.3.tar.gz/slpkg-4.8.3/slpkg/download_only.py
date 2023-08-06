#!/usr/bin/python3
# -*- coding: utf-8 -*-

import time
import shutil
from pathlib import Path

from slpkg.configs import Configs
from slpkg.utilities import Utilities
from slpkg.downloader import Downloader
from slpkg.views.views import ViewMessage
from slpkg.repositories import Repositories
from slpkg.models.models import session as Session


class DownloadOnly(Configs):
    """ Download only the sources and the slackbuilds or the packages
        for binary repositories.
    """

    def __init__(self, directory: Path, flags: list, data: dict, repository: str):
        super(Configs, self).__init__()
        self.directory: Path = directory
        self.flags: list = flags
        self.data: dict = data
        self.repository: str = repository

        self.view = ViewMessage(flags, repository, data)
        self.repos = Repositories()
        self.utils = Utilities()
        self.session = Session
        self.urls: list = []
        self.download_path: Path = Path()

        self.sbo_repo: dict = {
            self.repos.sbo_repo_name: self.repos.sbo_repo_path,
            self.repos.ponce_repo_name: self.repos.ponce_repo_path
        }

        self.is_binary: bool = self.utils.is_binary_repo(repository)
        self.option_for_directory: bool = self.utils.is_option(
            ['-z', '--directory='], flags)

    def packages(self, packages: list) -> None:
        packages: list = self.utils.apply_package_pattern(self.data, packages)
        self.view.download_packages(packages, self.directory)
        self.view.question()
        self.set_download_path()
        start: float = time.time()

        for pkg in packages:
            if self.is_binary:
                self.save_binary_sources(pkg)
            else:
                self.save_slackbuild_sources(pkg)
                self.copy_slackbuild_scripts(pkg)

        self.download_the_sources()

        elapsed_time: float = time.time() - start
        self.utils.finished_time(elapsed_time)

    def set_download_path(self) -> None:
        self.download_path: Path = self.download_only_path
        if self.option_for_directory:
            self.download_path: Path = self.directory

    def save_binary_sources(self, name: str) -> None:
        package: str = self.data[name]['package']
        mirror: str = self.data[name]['mirror']
        location: str = self.data[name]['location']
        self.urls.append(f'{mirror}{location}/{package}')

    def save_slackbuild_sources(self, name: str) -> None:
        if self.os_arch == 'x86_64' and self.data[name]['download64']:
            sources: list = self.data[name]['download64'].split()
        else:
            sources: list = self.data[name]['download'].split()
        self.urls.extend(sources)

    def copy_slackbuild_scripts(self, name: str) -> None:
        repo_path_package: Path = Path(self.sbo_repo[self.repository], self.data[name]['location'], name)
        if not Path(self.download_path, name).is_dir():
            shutil.copytree(repo_path_package, Path(self.download_path, name))
        print(f"{self.byellow}Copying{self.endc}: {repo_path_package} -> {Path(self.download_path, name)}")

    def download_the_sources(self) -> None:
        print('\nDownloading the sources:')
        down = Downloader(self.download_path, self.urls, self.flags)
        down.download()

#!/usr/bin/python3
# -*- coding: utf-8 -*-

from pathlib import Path

from slpkg.configs import Configs
from slpkg.utilities import Utilities
from slpkg.repositories import Repositories


class ViewPackage(Configs):
    """ View the repository packages. """

    def __init__(self, flags: list, repository: str):
        super(Configs, self).__init__()
        self.flags: list = flags
        self.repository: str = repository

        self.utils = Utilities()
        self.repos = Repositories()

        self.option_for_pkg_version: bool = self.utils.is_option(
            ['-p', '--pkg-version'], flags)

    def slackbuild(self, data: dict, slackbuilds: list) -> None:
        """ View slackbuild packages information. """
        repo: dict = {
            self.repos.sbo_repo_name: self.repos.sbo_repo_tar_suffix,
            self.repos.ponce_repo_name: str()
        }
        repo_tar_suffix: str = repo[self.repository]
        repository_packages: tuple = tuple(data.keys())

        for sbo in slackbuilds:
            for name, item in data.items():

                if sbo == name or sbo == '*':
                    path_file: Path = Path(self.repos.repositories[self.repository]['path'],
                                           item['location'], name, 'README')
                    readme: list = self.utils.read_text_file(path_file)

                    path_info: Path = Path(self.repos.repositories[self.repository]['path'],
                                           item['location'], name, f'{name}.info')
                    info_file: list = self.utils.read_text_file(path_info)

                    repo_build_tag: str = self.utils.read_slackbuild_build_tag(
                        name, item['location'], self.repository)

                    mirror: str = self.repos.repositories[self.repository]['mirror'][0]

                    maintainer = email = homepage = str()
                    for line in info_file:
                        if line.startswith('HOMEPAGE'):
                            homepage: str = line[10:-2].strip()
                        if line.startswith('MAINTAINER'):
                            maintainer: str = line[12:-2].strip()
                        if line.startswith('EMAIL'):
                            email: str = line[7:-2].strip()

                    deps: str = (', '.join([f'{self.cyan}{pkg}' for pkg in item['requires'].split()]))
                    if self.option_for_pkg_version:
                        deps: str = (', '.join(
                            [f"{self.cyan}{pkg}{self.endc}-{self.yellow}{data[pkg]['version']}"
                             f"{self.green}" for pkg in item['requires'].split()
                             if pkg in repository_packages]))

                    print(f"Name: {self.green}{name}{self.endc}\n"
                          f"Version: {self.green}{item['version']}{self.endc}\n"
                          f"Build: {self.green}{repo_build_tag}{self.endc}\n"
                          f"Requires: {self.green}{deps}{self.endc}\n"
                          f"Homepage: {self.blue}{homepage}{self.endc}\n"
                          f"Download SlackBuild: {self.blue}{mirror}"
                          f"{item['location']}/{name}{repo_tar_suffix}{self.endc}\n"
                          f"Download sources: {self.blue}{item['download']}{self.endc}\n"
                          f"Download_x86_64 sources: {self.blue}{item['download64']}{self.endc}\n"
                          f"Md5sum: {self.yellow}{item['md5sum']}{self.endc}\n"
                          f"Md5sum_x86_64: {self.yellow}{item['md5sum64']}{self.endc}\n"
                          f"Files: {self.green}{item['files']}{self.endc}\n"
                          f"Description: {self.green}{item['description']}{self.endc}\n"
                          f"Category: {self.red}{item['location']}{self.endc}\n"
                          f"SBo url: {self.blue}{mirror}{item['location']}/{name}{self.endc}\n"
                          f"Maintainer: {self.yellow}{maintainer}{self.endc}\n"
                          f"Email: {self.yellow}{email}{self.endc}\n"
                          f"\nREADME: {self.cyan}{''.join(readme)}{self.endc}")

    def package(self, data: dict, packages: list) -> None:
        """ View binary packages information. """
        repository_packages: tuple = tuple(data.keys())
        for package in packages:
            for name, item in data.items():

                if package == name or package == '*':
                    deps: str = (', '.join([f"{self.cyan}{pkg}" for pkg in item['requires'].split()]))
                    if self.option_for_pkg_version:
                        deps: str = (', '.join(
                            [f"{self.cyan}{pkg}{self.endc} {self.yellow}{data[pkg]['requires']}"
                             f"{self.green}" for pkg in item['requires'].split()
                             if pkg in repository_packages]))

                    print(f"Name: {self.green}{name}{self.endc}\n"
                          f"Version: {self.green}{item['version']}{self.endc}\n"
                          f"Package: {self.cyan}{item['package']}{self.endc}\n"
                          f"Download: {self.blue}{item['mirror']}{item['location']}/{item['package']}{self.endc}\n"
                          f"Md5sum: {item['checksum']}\n"
                          f"Mirror: {self.blue}{item['mirror']}{self.endc}\n"
                          f"Location: {self.red}{item['location']}{self.endc}\n"
                          f"Size Comp: {self.yellow}{item['size_comp']} KB{self.endc}\n"
                          f"Size Uncomp: {self.yellow}{item['size_uncomp']} KB{self.endc}\n"
                          f"Requires: {self.green}{deps}{self.endc}\n"
                          f"Conflicts: {item['conflicts']}\n"
                          f"Suggests: {item['suggests']}\n"
                          f"Description: {item['description']}\n")

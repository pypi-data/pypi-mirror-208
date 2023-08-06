#!/usr/bin/python3
# -*- coding: utf-8 -*-

from typing import Generator

from slpkg.repositories import Repositories


class Required:
    """ Creates a tuple of dependencies with
    the right order to install. """
    __slots__ = (
        'data', 'name', 'repos',
        'special_repos', 'repo', 'repository_packages'
    )

    def __init__(self, data: dict, name: str):
        self.data: dict = data
        self.name: str = name
        self.repos = Repositories()

        self.special_repos: list = [
            self.repos.salixos_repo_name,
            self.repos.salixos_patches_repo_name,
            self.repos.salixos_extra_repo_name,
            self.repos.slackel_repo_name,
            self.repos.slint_repo_name
        ]

        self.repo: str = data[name]['repository']
        self.repository_packages: tuple = tuple(self.data.keys())

    def resolve(self) -> tuple:
        """ Resolve the dependencies. """
        requires: list[str] = list(
            self.remove_deps(self.data[self.name]['requires'].split())
        )

        # Resolve dependencies for some special repos.
        if self.repo in self.special_repos:
            for require in requires:
                if require not in self.repository_packages:
                    requires.remove(require)

        else:
            for require in requires:
                sub_requires: list[str] = list(
                    self.remove_deps(self.data[require]['requires'].split())
                )
                for sub in sub_requires:
                    requires.append(sub)

        requires.reverse()
        return tuple(dict.fromkeys(requires))

    def remove_deps(self, requires: list) -> Generator:
        """ Remove requires that not in the repository or blacklisted. """
        for dependency in requires:
            if dependency in self.repository_packages:
                yield dependency

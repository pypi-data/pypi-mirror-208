#!/usr/bin/python3
# -*- coding: utf-8 -*-

from typing import Generator


class Requires:
    """ Creates a tuple of dependencies with
    the right order to install. """
    __slots__ = ('data', 'name', 'repository_packages')

    def __init__(self, data: dict, name: str):
        self.data: dict = data
        self.name: str = name
        self.repository_packages: tuple = tuple(data.keys())

    def resolve(self) -> tuple:
        """ Resolve the dependencies. """
        requires: list[str] = list(
            self.remove_deps(self.data[self.name]['requires'].split())
        )

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

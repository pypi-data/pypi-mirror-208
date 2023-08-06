#!/usr/bin/python3
# -*- coding: utf-8 -*-

from slpkg.utilities import Utilities
from slpkg.binaries.required import Required
from slpkg.sbos.dependencies import Requires
from slpkg.models.models import LogsDependencies
from slpkg.models.models import session as Session


class LoggingDeps:
    """ Logging installed dependencies. """

    def __init__(self, repository: str, data: dict):
        self.data: dict = data

        self.utils = Utilities()
        self.session = Session

        self.is_binary: bool = self.utils.is_binary_repo(repository)

    def logging(self, name: str) -> None:
        exist = self.session.query(LogsDependencies.name).filter(
            LogsDependencies.name == name).first()

        if self.is_binary:
            requires: tuple = Required(self.data, name).resolve()
        else:
            requires: tuple = Requires(self.data, name).resolve()

        # Update the dependencies if exist else create it.
        if exist:
            self.session.query(
                LogsDependencies).filter(
                LogsDependencies.name == name).update(
                {LogsDependencies.requires: ' '.join(requires)})

        elif requires:
            deps: list = LogsDependencies(name=name, requires=' '.join(requires))
            self.session.add(deps)
        self.session.commit()

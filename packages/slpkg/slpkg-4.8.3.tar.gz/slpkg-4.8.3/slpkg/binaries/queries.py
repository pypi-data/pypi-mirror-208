#!/usr/bin/python3
# -*- coding: utf-8 -*-

from slpkg.utilities import Utilities
from slpkg.models.models import BinariesTable
from slpkg.models.models import session as Session


class BinQueries:
    """ Queries class for the binary repositories. """

    def __init__(self, repository: str):
        self.repository: str = repository
        self.session = Session

        self.utils = Utilities()

    def repository_data(self) -> dict:
        """ Returns a dictionary with the repository data. """
        repository_data: tuple = self.session.query(
            BinariesTable).where(
            BinariesTable.repo == self.repository).all()

        repos_dict: dict[str] = {
            data.name: {'version': data.version,
                        'package': data.package,
                        'mirror': data.mirror,
                        'location': data.location,
                        'size_comp': data.size_comp,
                        'size_uncomp': data.size_uncomp,
                        'requires': data.required,
                        'conflicts': data.conflicts,
                        'suggests': data.suggests,
                        'description': data.description,
                        'checksum': data.checksum,
                        'repository': data.repo}
            for data in repository_data
            if not self.utils.blacklist_pattern(data.name)
        }

        return repos_dict

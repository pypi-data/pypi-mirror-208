#!/usr/bin/python3
# -*- coding: utf-8 -*-

from slpkg.configs import Configs
from slpkg.utilities import Utilities
from slpkg.repositories import Repositories
from slpkg.models.models import session as Session
from slpkg.models.models import SBoTable, PonceTable


class SBoQueries(Configs):
    """ Queries class for the sbo repository. """

    def __init__(self, repository: str):
        super(Configs, self).__init__()
        self.session = Session

        self.repos = Repositories()
        self.utils = Utilities()

        table: dict = {
            self.repos.sbo_repo_name: SBoTable,
            self.repos.ponce_repo_name: PonceTable
        }

        if repository == '*':
            repository = self.repos.default_repository

        self.sbo_table: str = table[repository]

    def repository_data(self) -> dict:
        """ Returns a dictionary with the repository data. """
        repository_data: tuple = self.session.query(self.sbo_table).all()

        repos_dict: dict[str] = {
            data.name: {'location': data.location,
                        'files': data.files,
                        'version': data.version,
                        'download': data.download,
                        'download64': data.download64,
                        'md5sum': data.md5sum,
                        'md5sum64': data.md5sum64,
                        'requires': data.requires,
                        'description': data.short_description}
            for data in repository_data
            if not self.utils.blacklist_pattern(data.name)
        }
        return repos_dict

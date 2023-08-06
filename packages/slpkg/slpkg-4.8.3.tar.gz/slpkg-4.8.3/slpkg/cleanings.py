#!/usr/bin/python3
# -*- coding: utf-8 -*-

import shutil
from pathlib import PosixPath

from slpkg.configs import Configs
from slpkg.utilities import Utilities
from slpkg.views.views import ViewMessage
from slpkg.repositories import Repositories
from slpkg.models.models import session as Session
from slpkg.models.models import (Base, engine, LogsDependencies,
                                 SBoTable, PonceTable, BinariesTable,
                                 LastRepoUpdated)


class Cleanings(Configs):
    """ Cleans the logs from packages. """

    def __init__(self, flags: list):
        super(Configs, self).__init__()
        self.flags: list = flags
        self.session = Session

        self.view = ViewMessage(flags)
        self.repos = Repositories()
        self.utils = Utilities()

    def tmp(self) -> None:
        print('Deleting of local data:\n')

        for file in self.tmp_slpkg.glob('*'):
            print(f"  {self.bred}>{self.endc} '{file}'")

        print(f"\n{self.prog_name}: {self.blink}{self.bold}{self.bred}WARNING!{self.endc}: All the files and "
              f"folders will delete!")

        self.view.question()

        self.utils.remove_folder_if_exists(self.tmp_slpkg)
        self.utils.create_directory(self.build_path)
        print(f'{self.byellow}Successfully cleared!{self.endc}\n')

    def logs_dependencies(self) -> None:
        """ Deletes the log table from the database. """
        dependencies: list = self.session.query(
            LogsDependencies.name, LogsDependencies.requires).all()  # type: ignore

        if dependencies:
            self.view.logs_dependencies(dependencies)
            self.view.question()
            self.delete_logs_of_dependencies()
        else:
            print('\nNothing to clean.\n')

    def delete_logs_of_dependencies(self):
        self.session.query(LogsDependencies).delete()
        self.session.commit()

    def db_tables(self) -> None:
        """ Drop all the tables from the database. """
        print('Deleting repositories of local data and the database:\n')
        for item in self.repos.repositories.values():
            if item['path'].exists() and isinstance(item['path'], PosixPath):
                print(f"  {self.bred}>{self.endc} '{item['path']}'")

        print(f'\n{self.prog_name}: {self.blink}{self.bold}{self.bred}WARNING!{self.endc}: '
              f'All the data from the database will be deleted!')
        self.view.question()

        tables: list = [
            PonceTable.__table__,
            SBoTable.__table__,
            BinariesTable.__table__,
            LastRepoUpdated.__table__
        ]

        Base.metadata.drop_all(bind=engine, tables=tables)

        # Deletes local downloaded data.
        self.delete_repositories_data()

        print(f"{self.byellow}Successfully cleared!{self.endc}\n\n"
              "You need to update the package lists now:\n\n"
              "  $ slpkg update\n")

    def delete_repositories_data(self) -> None:
        """ Deletes local folders with the repository downloaded data. """
        for item in self.repos.repositories.values():
            if item['path'].exists() and isinstance(item['path'], PosixPath):
                shutil.rmtree(item['path'])

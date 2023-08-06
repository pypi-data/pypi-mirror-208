#!/usr/bin/python3
# -*- coding: utf-8 -*-

from typing import NoReturn
from slpkg.configs import Configs
from slpkg.views.version import Version


class Usage(Configs):

    def __init__(self):
        super(Configs, self).__init__()

    def help_minimal(self, message: str) -> NoReturn:
        """ Prints the minimal help menu. """
        print(message)
        args: str = (
            f'\nUsage: {self.prog_name} [{self.cyan}COMMAND{self.endc}] [{self.yellow}OPTIONS{self.endc}] '
            f'[FILELIST|PACKAGES...]\n'
            f"\nTry '{self.prog_name} --help' for more options.\n")

        print(args)
        raise SystemExit(1)

    def help_short(self, status: int) -> NoReturn:
        """ Prints the short menu. """
        args: str = (
            f'USAGE: {self.prog_name} [{self.cyan}COMMAND{self.endc}] [{self.yellow}OPTIONS{self.endc}] '
            f'[FILELIST|PACKAGES...]\n'
            f'\n  slpkg [{self.cyan}COMMAND{self.endc}] [-u, update, -U, upgrade, -c, check-updates, -I, repo-info]\n'
            f'  slpkg [{self.cyan}COMMAND{self.endc}] [-g, configs, -L, clean-logs, -T, clean-data, -D, clean-tmp]\n'
            f'  slpkg [{self.cyan}COMMAND{self.endc}] [-b, build, -i, install, -R, remove [PACKAGES...]]\n'
            f'  slpkg [{self.cyan}COMMAND{self.endc}] [-d, download, -f, find, -w, view [PACKAGES...]]\n'
            f'  slpkg [{self.cyan}COMMAND{self.endc}] [-s, search, -e, dependees, -t, tracking  [PACKAGES...]]\n'
            f'  slpkg [{self.yellow}OPTIONS{self.endc}] [-y, --yes, -j, --jobs, -O, --resolve-off, -r, --reinstall]\n'
            f'  slpkg [{self.yellow}OPTIONS{self.endc}] [-k, --skip-installed, -a, --install-data]\n'
            f'  slpkg [{self.yellow}OPTIONS{self.endc}] [-E, --full-reverse, -S, --search, -n, --no-silent]\n'
            f'  slpkg [{self.yellow}OPTIONS{self.endc}] [-p, --pkg-version, -P, --parallel]\n'
            f'  slpkg [{self.yellow}OPTIONS{self.endc}] [-o, --repository=NAME, -z, --directory=PATH]\n'
            "  \nIf you need more information please try 'slpkg --help'.")

        print(args)
        raise SystemExit(status)

    def help(self, status: int) -> NoReturn:
        """ Prints the main menu. """
        args: str = (
            f'{self.prog_name} - version {Version().version}\n\n'
            f'{self.bold}USAGE:{self.endc}\n  {self.prog_name} [{self.cyan}COMMAND{self.endc}] '
            f'[{self.yellow}OPTIONS{self.endc}] [FILELIST|PACKAGES...]\n'
            f'\n{self.bold}DESCRIPTION:{self.endc}\n  Package manager utility for Slackware.\n'
            f'\n{self.bold}COMMANDS:{self.endc}\n'
            f'  {self.red}-u, update{self.endc}                    Update the package lists.\n'
            f'  {self.cyan}-U, upgrade{self.endc}                   Upgrade all the packages.\n'
            f'  {self.cyan}-c, check-updates{self.endc}             Check for news on ChangeLog.txt.\n'
            f'  {self.cyan}-I, repo-info{self.endc}                 Prints the repositories information.\n'
            f'  {self.cyan}-g, configs{self.endc}                   Edit the configuration file.\n'
            f'  {self.cyan}-L, clean-logs{self.endc}                Clean dependencies log tracking.\n'
            f'  {self.cyan}-T, clean-data{self.endc}                Clean all the repositories data.\n'
            f'  {self.cyan}-D, clean-tmp{self.endc}                 Delete all the downloaded sources.\n'
            f'  {self.cyan}-b, build{self.endc} [PACKAGES...]       Build only the packages.\n'
            f'  {self.cyan}-i, install{self.endc} [PACKAGES...]     Build and install the packages.\n'
            f'  {self.cyan}-R, remove{self.endc} [PACKAGES...]      Remove installed packages.\n'
            f'  {self.cyan}-d, download{self.endc} [PACKAGES...]    Download only the scripts and sources.\n'
            f'  {self.cyan}-f, find{self.endc} [PACKAGES...]        Find installed packages.\n'
            f'  {self.cyan}-w, view{self.endc} [PACKAGES...]        View packages from the repository.\n'
            f'  {self.cyan}-s, search{self.endc} [PACKAGES...]      Search packages from the repository.\n'
            f'  {self.cyan}-e, dependees{self.endc} [PACKAGES...]   Show which packages depend on.\n'
            f'  {self.cyan}-t, tracking{self.endc} [PACKAGES...]    Tracking the packages dependencies.\n'
            f'\n{self.bold}OPTIONS:{self.endc}\n'
            f'  {self.yellow}-y, --yes{self.endc}                     Answer Yes to all questions.\n'
            f'  {self.yellow}-j, --jobs{self.endc}                    Set it for multicore systems.\n'
            f'  {self.yellow}-O, --resolve-off{self.endc}             Turns off dependency resolving.\n'
            f'  {self.yellow}-r, --reinstall{self.endc}               Upgrade packages of the same version.\n'
            f'  {self.yellow}-k, --skip-installed{self.endc}          Skip installed packages.\n'
            f'  {self.yellow}-a, --install-data{self.endc}            Install data into the database only.\n'
            f'  {self.yellow}-E, --full-reverse{self.endc}            Full reverse dependency.\n'
            f'  {self.yellow}-S, --search{self.endc}                  Search packages from the repository.\n'
            f'  {self.yellow}-n, --no-silent{self.endc}               Disable silent mode.\n'
            f'  {self.yellow}-p, --pkg-version{self.endc}             Print the repository package version.\n'
            f'  {self.yellow}-P, --parallel{self.endc}                Download files in parallel.\n'
            f'  {self.yellow}-o, --repository={self.endc}NAME         Change repository you want to work.\n'
            f'  {self.yellow}-z, --directory={self.endc}PATH          Download files to a specific path.\n'
            '\n  -h, --help                    Show this message and exit.\n'
            '  -v, --version                 Print version and exit.\n'
            "\nIf you need more information try to use slpkg manpage.\n"
            "Extra help for the commands, use: 'slpkg help [COMMAND]'.\n"
            "Edit the config file in the /etc/slpkg/slpkg.toml or 'slpkg configs'.")

        print(args)
        raise SystemExit(status)

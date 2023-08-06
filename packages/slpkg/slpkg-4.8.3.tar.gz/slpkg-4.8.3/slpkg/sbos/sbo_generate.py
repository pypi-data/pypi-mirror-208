#!/usr/bin/python3
# -*- coding: utf-8 -*-

from pathlib import Path
from slpkg.configs import Configs


class SBoGenerate(Configs):
    """ Generating the SLACKBUILDS.TXT file. """

    def __init__(self):
        super(Configs, self).__init__()

    def slackbuild_file(self, repo_path: Path, repo_slackbuild_txt: str) -> None:
        print(f'Generating the {repo_slackbuild_txt} file... ', end='', flush=True)

        # slackbuild.info variables
        info_var: dict[int] = {
            1: 'PRGNAM=',
            2: 'VERSION=',
            3: 'HOMEPAGE=',
            4: 'DOWNLOAD=',
            5: 'MD5SUM=',
            6: 'DOWNLOAD_x86_64=',
            7: 'MD5SUM_x86_64=',
            8: 'REQUIRES=',
            9: 'MAINTAINER=',
            10: 'EMAIL='
        }

        with open(Path(repo_path, repo_slackbuild_txt), 'w') as sbo:
            for path in repo_path.glob('**/*'):
                if path.name.endswith('.info'):
                    sbo_path = Path('/'.join(str(path).split('/')[:-1]))

                    name: str = str(path).split('/')[-2]
                    location: str = str(Path('/'.join(str(path).split('/')[-3:-1])))
                    files: str = ' '.join([file.name for file in list(sbo_path.iterdir())])

                    version: str = (
                        ' '.join([var.strip() for var in self.read_info_file(
                            path, info_var[2], info_var[3])])[len(info_var[2]):].replace('"', ''))

                    download: str = (
                        ' '.join([var.replace('\\', '').strip() for var in self.read_info_file(
                            path, info_var[4], info_var[5])])[len(info_var[4]):].replace('"', ''))

                    download_x86_64: str = (
                        ' '.join([var.replace('\\', '').strip() for var in self.read_info_file(
                            path, info_var[6], info_var[7])])[len(info_var[6]):].replace('"', ''))

                    md5sum: str = (
                        ' '.join([var.replace('\\', '').strip() for var in self.read_info_file(
                            path, info_var[5], info_var[6])])[len(info_var[5]):].replace('"', ''))

                    md5sum_x86_64: str = (
                        ' '.join([var.replace('\\', '').strip() for var in self.read_info_file(
                            path, info_var[7], info_var[8])])[len(info_var[7]):].replace('"', ''))

                    requires: str = (' '.join([var for var in self.read_info_file(
                        path, info_var[8], info_var[9])])[len(info_var[8]):].replace('"', ''))

                    short_description: str = self.read_short_description(sbo_path, name)

                    sbo.write(f'SLACKBUILD NAME: {name}\n')
                    sbo.write(f'SLACKBUILD LOCATION: ./{location}\n')
                    sbo.write(f'SLACKBUILD FILES: {files}\n')
                    sbo.write(f'SLACKBUILD VERSION: {version}\n')
                    sbo.write(f'SLACKBUILD DOWNLOAD: {download}\n')
                    sbo.write(f'SLACKBUILD DOWNLOAD_x86_64: {download_x86_64}\n')
                    sbo.write(f'SLACKBUILD MD5SUM: {md5sum}\n')
                    sbo.write(f'SLACKBUILD MD5SUM_x86_64: {md5sum_x86_64}\n')
                    sbo.write(f'SLACKBUILD REQUIRES: {requires}\n')
                    sbo.write(f'SLACKBUILD SHORT DESCRIPTION: {short_description}\n')
                    sbo.write('\n')

        print(f'{self.byellow}Done{self.endc}\n')

    @staticmethod
    def read_short_description(path: Path, name: str) -> str:
        """ Returns the short description. """
        slack_desc: Path = Path(path, 'slack-desc')
        if slack_desc.is_file():
            with open(slack_desc, 'r') as f:
                slack = f.readlines()

            for line in slack:
                pattern: str = f'{name}: {name}'
                if line.startswith(pattern):
                    return line[len(name) + 1:].strip()
        return str()

    @staticmethod
    def read_info_file(info_file: Path, start: str, stop: str) -> list:
        """ Reads the .info file and return the line between to variables. """
        begin = end = 0
        with open(info_file, 'r') as f:
            info = f.read().splitlines()

        for index, line in enumerate(info):
            if line.startswith(start):
                begin = index
            if line.startswith(stop):
                end = index
                break

        return info[begin:end]

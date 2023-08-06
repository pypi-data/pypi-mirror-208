#!/usr/bin/python3
# -*- coding: utf-8 -*-


import tomli
from pathlib import Path
from dataclasses import dataclass

from slpkg.configs import Configs
from slpkg.toml_error_message import TomlErrors


@dataclass
class Repositories:
    errors = TomlErrors()

    repositories_toml_file: Path = Path(Configs.etc_path, 'repositories.toml')
    repositories_path: Path = Path(Configs.lib_path, 'repositories')

    repos_config = {}
    repositories = {}

    default_repository: str = 'sbo'

    sbo_repo: bool = True
    sbo_repo_name: str = 'sbo'
    sbo_repo_path: Path = Path(repositories_path, sbo_repo_name)
    sbo_repo_local = ['']
    sbo_repo_mirror = ['https://slackbuilds.org/slackbuilds/15.0/']
    sbo_repo_slackbuilds: str = 'SLACKBUILDS.TXT'
    sbo_repo_changelog: str = 'ChangeLog.txt'
    sbo_repo_tag: str = '_SBo'
    sbo_repo_patch_tag: str = ''
    sbo_repo_tar_suffix: str = '.tar.gz'

    ponce_repo: bool = False
    ponce_repo_name: str = 'ponce'
    ponce_repo_path: Path = Path(repositories_path, ponce_repo_name)
    ponce_repo_local = ['']
    ponce_repo_mirror = ['https://cgit.ponce.cc/slackbuilds/plain/']
    ponce_repo_slackbuilds: str = 'SLACKBUILDS.TXT'
    ponce_repo_changelog: str = 'ChangeLog.txt'
    ponce_repo_tag: str = '_SBo'
    ponce_repo_patch_tag: str = ''

    slack_repo: bool = False
    slack_repo_name: str = 'slack'
    slack_repo_path: Path = Path(repositories_path, slack_repo_name)
    slack_repo_local = ['']
    slack_repo_mirror = ['https://slackware.uk/slackware/slackware64-15.0/']
    slack_repo_packages: str = 'PACKAGES.TXT'
    slack_repo_checksums: str = 'CHECKSUMS.md5'
    slack_repo_changelog: str = 'ChangeLog.txt'
    slack_repo_tag: str = ''

    slack_extra_repo: bool = False
    slack_extra_repo_name: str = 'slack_extra'
    slack_extra_repo_path: Path = Path(repositories_path, slack_extra_repo_name)
    slack_extra_repo_local = ['']
    slack_extra_repo_mirror = ['https://slackware.uk/slackware/slackware64-15.0/', "extra/"]
    slack_extra_repo_packages: str = 'PACKAGES.TXT'
    slack_extra_repo_checksums: str = 'CHECKSUMS.md5'
    slack_extra_repo_changelog: str = 'ChangeLog.txt'
    slack_extra_repo_tag: str = ''

    slack_patches_repo: bool = False
    slack_patches_repo_name: str = 'slack_patches'
    slack_patches_repo_path: Path = Path(repositories_path, slack_patches_repo_name)
    slack_patches_repo_local = ['']
    slack_patches_repo_mirror = ['https://slackware.uk/slackware/slackware64-15.0/', 'patches/']
    slack_patches_repo_packages: str = 'PACKAGES.TXT'
    slack_patches_repo_checksums: str = 'CHECKSUMS.md5'
    slack_patches_repo_changelog: str = 'ChangeLog.txt'
    slack_patches_repo_tag: str = '_slack15.0'

    alien_repo: bool = False
    alien_repo_name: str = 'alien'
    alien_repo_path: Path = Path(repositories_path, alien_repo_name)
    alien_repo_local = ['']
    alien_repo_mirror = ['https://slackware.nl/people/alien/sbrepos/', '15.0/', 'x86_64/']
    alien_repo_packages: str = 'PACKAGES.TXT'
    alien_repo_checksums: str = 'CHECKSUMS.md5'
    alien_repo_changelog: str = 'ChangeLog.txt'
    alien_repo_tag: str = 'alien'

    multilib_repo: bool = False
    multilib_repo_name: str = 'multilib'
    multilib_repo_path: Path = Path(repositories_path, multilib_repo_name)
    multilib_repo_local = ['']
    multilib_repo_mirror = ['https://slackware.nl/people/alien/multilib/', '15.0/']
    multilib_repo_packages: str = 'PACKAGES.TXT'
    multilib_repo_checksums: str = 'CHECKSUMS.md5'
    multilib_repo_changelog: str = 'ChangeLog.txt'
    multilib_repo_tag: str = 'alien'

    restricted_repo: bool = False
    restricted_repo_name: str = 'restricted'
    restricted_repo_path: Path = Path(repositories_path, restricted_repo_name)
    restricted_repo_local = ['']
    restricted_repo_mirror = ['https://slackware.nl/people/alien/restricted_sbrepos/', '15.0/', 'x86_64/']
    restricted_repo_packages: str = 'PACKAGES.TXT'
    restricted_repo_checksums: str = 'CHECKSUMS.md5'
    restricted_repo_changelog: str = 'ChangeLog.txt'
    restricted_repo_tag: str = 'alien'

    gnome_repo: bool = False
    gnome_repo_name: str = 'gnome'
    gnome_repo_path: Path = Path(repositories_path, gnome_repo_name)
    gnome_repo_local = ['']
    gnome_repo_mirror = ['https://reddoglinux.ddns.net/linux/gnome/43.x/x86_64/']
    gnome_repo_packages: str = 'PACKAGES.TXT'
    gnome_repo_checksums: str = 'CHECKSUMS.md5'
    gnome_repo_changelog: str = 'ChangeLog.txt'
    gnome_repo_tag: str = 'gfs'

    msb_repo: bool = False
    msb_repo_name: str = 'msb'
    msb_repo_path: Path = Path(repositories_path, msb_repo_name)
    msb_repo_local = ['']
    msb_repo_mirror = ['https://slackware.uk/msb/', '15.0/', '1.26/', 'x86_64/']
    msb_repo_packages: str = 'PACKAGES.TXT'
    msb_repo_checksums: str = 'CHECKSUMS.md5'
    msb_repo_changelog: str = 'ChangeLog.txt'
    msb_repo_tag: str = 'msb'

    csb_repo: bool = False
    csb_repo_name: str = 'csb'
    csb_repo_path: Path = Path(repositories_path, csb_repo_name)
    csb_repo_local = ['']
    csb_repo_mirror = ['https://slackware.uk/csb/', '15.0/', 'x86_64/']
    csb_repo_packages: str = 'PACKAGES.TXT'
    csb_repo_checksums: str = 'CHECKSUMS.md5'
    csb_repo_changelog: str = 'ChangeLog.txt'
    csb_repo_tag: str = 'csb'

    conraid_repo: bool = False
    conraid_repo_name: str = 'conraid'
    conraid_repo_path: Path = Path(repositories_path, conraid_repo_name)
    conraid_repo_local = ['']
    conraid_repo_mirror = ['https://slack.conraid.net/repository/slackware64-current/']
    conraid_repo_packages: str = 'PACKAGES.TXT'
    conraid_repo_checksums: str = 'CHECKSUMS.md5'
    conraid_repo_changelog: str = 'ChangeLog.txt'
    conraid_repo_tag: str = 'cf'

    slackonly_repo: bool = False
    slackonly_repo_name: str = 'slackonly'
    slackonly_repo_path: Path = Path(repositories_path, slackonly_repo_name)
    slackonly_repo_local = ['']
    slackonly_repo_mirror = ['https://packages.slackonly.com/pub/packages/15.0-x86_64/']
    slackonly_repo_packages: str = 'PACKAGES.TXT'
    slackonly_repo_checksums: str = 'CHECKSUMS.md5'
    slackonly_repo_changelog: str = 'ChangeLog.txt'
    slackonly_repo_tag: str = 'slonly'

    salixos_repo: bool = False
    salixos_repo_name: str = 'salixos'
    salixos_repo_path: Path = Path(repositories_path, salixos_repo_name)
    salixos_repo_local = ['']
    salixos_repo_mirror = ['https://download.salixos.org/x86_64/slackware-15.0/']
    salixos_repo_packages: str = 'PACKAGES.TXT'
    salixos_repo_checksums: str = 'CHECKSUMS.md5'
    salixos_repo_changelog: str = 'ChangeLog.txt'
    salixos_repo_tag: str = ''

    salixos_extra_repo: bool = False
    salixos_extra_repo_name: str = 'salixos_extra'
    salixos_extra_repo_path: Path = Path(repositories_path, salixos_extra_repo_name)
    salixos_extra_repo_local = ['']
    salixos_extra_repo_mirror = ['https://download.salixos.org/x86_64/slackware-15.0/', 'extra/']
    salixos_extra_repo_packages: str = 'PACKAGES.TXT'
    salixos_extra_repo_checksums: str = 'CHECKSUMS.md5'
    salixos_extra_repo_changelog: str = 'ChangeLog.txt'
    salixos_extra_repo_tag: str = ''

    salixos_patches_repo: bool = False
    salixos_patches_repo_name: str = 'salixos_patches'
    salixos_patches_repo_path: Path = Path(repositories_path, salixos_patches_repo_name)
    salixos_patches_repo_local = ['']
    salixos_patches_repo_mirror = ['https://download.salixos.org/x86_64/slackware-15.0/', 'patches/']
    salixos_patches_repo_packages: str = 'PACKAGES.TXT'
    salixos_patches_repo_checksums: str = 'CHECKSUMS.md5'
    salixos_patches_repo_changelog: str = 'ChangeLog.txt'
    salixos_patches_repo_tag: str = '_slack15.0'

    slackel_repo: bool = False
    slackel_repo_name: str = 'slackel'
    slackel_repo_path: Path = Path(repositories_path, slackel_repo_name)
    slackel_repo_local = ['']
    slackel_repo_mirror = ['http://www.slackel.gr/repo/x86_64/current/']
    slackel_repo_packages: str = 'PACKAGES.TXT'
    slackel_repo_checksums: str = 'CHECKSUMS.md5'
    slackel_repo_changelog: str = 'ChangeLog.txt'
    slackel_repo_tag: str = 'dj'

    slint_repo: bool = False
    slint_repo_name: str = 'slint'
    slint_repo_path: Path = Path(repositories_path, slint_repo_name)
    slint_repo_local = ['']
    slint_repo_mirror = ['https://slackware.uk/slint/x86_64/slint-15.0/']
    slint_repo_packages: str = 'PACKAGES.TXT'
    slint_repo_checksums: str = 'CHECKSUMS.md5'
    slint_repo_changelog: str = 'ChangeLog.txt'
    slint_repo_tag: str = 'slint'

    try:
        if repositories_toml_file.is_file():
            with open(repositories_toml_file, 'rb') as repo:
                repos_config = tomli.load(repo)['REPOSITORIES']

            default_repository: str = repos_config['DEFAULT_REPOSITORY']

            sbo_repo: str = repos_config['SBO_REPO']
            sbo_repo_name: str = repos_config['SBO_REPO_NAME']
            sbo_repo_local = repos_config['SBO_REPO_LOCAL']
            sbo_repo_mirror = repos_config['SBO_REPO_MIRROR']
            sbo_repo_slackbuilds: str = repos_config['SBO_REPO_SLACKBUILDS']
            sbo_repo_changelog: str = repos_config['SBO_REPO_CHANGELOG']
            sbo_repo_tag: str = repos_config['SBO_REPO_TAG']
            sbo_repo_patch_tag: str = repos_config['SBO_REPO_PATCH_TAG']
            sbo_repo_tar_suffix: str = repos_config['SBO_REPO_TAR_SUFFIX']
            try:
                if sbo_repo_local[0].startswith('file'):
                    sbo_repo_path: Path = Path(
                        ''.join(sbo_repo_local).replace('file:', '')
                    )
            except IndexError:
                sbo_repo_local = ['']

            ponce_repo: bool = repos_config['PONCE_REPO']
            ponce_repo_name: str = repos_config['PONCE_REPO_NAME']
            ponce_repo_local = repos_config['PONCE_REPO_LOCAL']
            ponce_repo_mirror = repos_config['PONCE_REPO_MIRROR']
            ponce_repo_slackbuilds: str = repos_config['PONCE_REPO_SLACKBUILDS']
            ponce_repo_changelog: str = repos_config['PONCE_REPO_CHANGELOG']
            ponce_repo_tag: str = repos_config['PONCE_REPO_TAG']
            ponce_repo_patch_tag: str = repos_config['PONCE_REPO_PATCH_TAG']
            try:
                if ponce_repo_local[0].startswith('file'):
                    ponce_repo_path: Path = Path(
                        ''.join(ponce_repo_local).replace('file:', '')
                    )
            except IndexError:
                ponce_repo_local = ['']

            slack_repo: bool = repos_config['SLACK_REPO']
            slack_repo_name: str = repos_config['SLACK_REPO_NAME']
            slack_repo_local = repos_config['SLACK_REPO_LOCAL']
            slack_repo_mirror = repos_config['SLACK_REPO_MIRROR']
            slack_repo_packages: str = repos_config['SLACK_REPO_PACKAGES']
            slack_repo_checksums: str = repos_config['SLACK_REPO_CHECKSUMS']
            slack_repo_changelog: str = repos_config['SLACK_REPO_CHANGELOG']
            slack_repo_tag: str = repos_config['SLACK_REPO_TAG']
            try:
                if slack_repo_local[0].startswith('file'):
                    slack_repo_path: Path = Path(
                        ''.join(slack_repo_local).replace('file:', '')
                    )
            except IndexError:
                slack_repo_local = ['']

            slack_extra_repo: bool = repos_config['SLACK_EXTRA_REPO']
            slack_extra_repo_name: str = repos_config['SLACK_EXTRA_REPO_NAME']
            slack_extra_repo_local = repos_config['SLACK_EXTRA_REPO_LOCAL']
            slack_extra_repo_mirror = repos_config['SLACK_EXTRA_REPO_MIRROR']
            slack_extra_repo_packages: str = repos_config['SLACK_EXTRA_REPO_PACKAGES']
            slack_extra_repo_checksums: str = repos_config['SLACK_EXTRA_REPO_CHECKSUMS']
            slack_extra_repo_changelog: str = repos_config['SLACK_EXTRA_REPO_CHANGELOG']
            slack_extra_repo_tag: str = repos_config['SLACK_EXTRA_REPO_TAG']
            try:
                if slack_extra_repo_local[0].startswith('file'):
                    slack_extra_repo_path: Path = Path(
                        ''.join(slack_extra_repo_local).replace('file:', '')
                    )
            except IndexError:
                slack_extra_repo_local = ['']

            slack_patches_repo: bool = repos_config['SLACK_PATCHES_REPO']
            slack_patches_repo_name: str = repos_config['SLACK_PATCHES_REPO_NAME']
            slack_patches_repo_local = repos_config['SLACK_PATCHES_REPO_LOCAL']
            slack_patches_repo_mirror = repos_config['SLACK_PATCHES_REPO_MIRROR']
            slack_patches_repo_packages: str = repos_config['SLACK_PATCHES_REPO_PACKAGES']
            slack_patches_repo_checksums: str = repos_config['SLACK_PATCHES_REPO_CHECKSUMS']
            slack_patches_repo_changelog: str = repos_config['SLACK_PATCHES_REPO_CHANGELOG']
            slack_patches_repo_tag: str = repos_config['SLACK_PATCHES_REPO_TAG']
            try:
                if slack_patches_repo_local[0].startswith('file'):
                    slack_patches_repo_path: Path = Path(
                        ''.join(slack_patches_repo_local).replace('file:', '')
                    )
            except IndexError:
                slack_patches_repo_local = ['']

            alien_repo: bool = repos_config['ALIEN_REPO']
            alien_repo_name: str = repos_config['ALIEN_REPO_NAME']
            alien_repo_local = repos_config['ALIEN_REPO_LOCAL']
            alien_repo_mirror = repos_config['ALIEN_REPO_MIRROR']
            alien_repo_packages: str = repos_config['ALIEN_REPO_PACKAGES']
            alien_repo_checksums: str = repos_config['ALIEN_REPO_CHECKSUMS']
            alien_repo_changelog: str = repos_config['ALIEN_REPO_CHANGELOG']
            alien_repo_tag: str = repos_config['ALIEN_REPO_TAG']
            try:
                if alien_repo_local[0].startswith('file'):
                    alien_repo_path: Path = Path(
                        ''.join(alien_repo_local).replace('file:', '')
                    )
            except IndexError:
                alien_repo_local = ['']

            multilib_repo: bool = repos_config['MULTILIB_REPO']
            multilib_repo_name: str = repos_config['MULTILIB_REPO_NAME']
            multilib_repo_local = repos_config['MULTILIB_REPO_LOCAL']
            multilib_repo_mirror = repos_config['MULTILIB_REPO_MIRROR']
            multilib_repo_packages: str = repos_config['MULTILIB_REPO_PACKAGES']
            multilib_repo_checksums: str = repos_config['MULTILIB_REPO_CHECKSUMS']
            multilib_repo_changelog: str = repos_config['MULTILIB_REPO_CHANGELOG']
            multilib_repo_tag: str = repos_config['MULTILIB_REPO_TAG']
            try:
                if multilib_repo_local[0].startswith('file'):
                    multilib_repo_path: Path = Path(
                        ''.join(multilib_repo_local).replace('file:', '')
                    )
            except IndexError:
                multilib_repo_local = ['']

            restricted_repo: bool = repos_config['RESTRICTED_REPO']
            restricted_repo_name: str = repos_config['RESTRICTED_REPO_NAME']
            restricted_repo_local = repos_config['RESTRICTED_REPO_LOCAL']
            restricted_repo_mirror = repos_config['RESTRICTED_REPO_MIRROR']
            restricted_repo_packages: str = repos_config['RESTRICTED_REPO_PACKAGES']
            restricted_repo_checksums: str = repos_config['RESTRICTED_REPO_CHECKSUMS']
            restricted_repo_changelog: str = repos_config['RESTRICTED_REPO_CHANGELOG']
            restricted_repo_tag: str = repos_config['RESTRICTED_REPO_TAG']
            try:
                if restricted_repo_local[0].startswith('file'):
                    restricted_repo_path: Path = Path(
                        ''.join(restricted_repo_local).replace('file:', '')
                    )
            except IndexError:
                restricted_repo_local = ['']

            gnome_repo: bool = repos_config['GNOME_REPO']
            gnome_repo_name: str = repos_config['GNOME_REPO_NAME']
            gnome_repo_local = repos_config['GNOME_REPO_LOCAL']
            gnome_repo_mirror = repos_config['GNOME_REPO_MIRROR']
            gnome_repo_packages: str = repos_config['GNOME_REPO_PACKAGES']
            gnome_repo_checksums: str = repos_config['GNOME_REPO_CHECKSUMS']
            gnome_repo_changelog: str = repos_config['GNOME_REPO_CHANGELOG']
            gnome_repo_tag: str = repos_config['GNOME_REPO_TAG']
            try:
                if gnome_repo_local[0].startswith('file'):
                    gnome_repo_path: Path = Path(
                        ''.join(gnome_repo_local).replace('file:', '')
                    )
            except IndexError:
                gnome_repo_local = ['']

            msb_repo: bool = repos_config['MSB_REPO']
            msb_repo_name: str = repos_config['MSB_REPO_NAME']
            msb_repo_local = repos_config['MSB_REPO_LOCAL']
            msb_repo_mirror = repos_config['MSB_REPO_MIRROR']
            msb_repo_packages: str = repos_config['MSB_REPO_PACKAGES']
            msb_repo_checksums: str = repos_config['MSB_REPO_CHECKSUMS']
            msb_repo_changelog: str = repos_config['MSB_REPO_CHANGELOG']
            msb_repo_tag: str = repos_config['MSB_REPO_TAG']
            try:
                if msb_repo_local[0].startswith('file'):
                    msb_repo_path: Path = Path(
                        ''.join(msb_repo_local).replace('file:', '')
                    )
            except IndexError:
                msb_repo_local = ['']

            csb_repo: bool = repos_config['CSB_REPO']
            csb_repo_name: str = repos_config['CSB_REPO_NAME']
            csb_repo_local = repos_config['CSB_REPO_LOCAL']
            csb_repo_mirror = repos_config['CSB_REPO_MIRROR']
            csb_repo_packages: str = repos_config['CSB_REPO_PACKAGES']
            csb_repo_checksums: str = repos_config['CSB_REPO_CHECKSUMS']
            csb_repo_changelog: str = repos_config['CSB_REPO_CHANGELOG']
            csb_repo_tag: str = repos_config['CSB_REPO_TAG']
            try:
                if csb_repo_local[0].startswith('file'):
                    csb_repo_path: Path = Path(
                        ''.join(csb_repo_local).replace('file:', '')
                    )
            except IndexError:
                csb_repo_local = ['']

            conraid_repo: bool = repos_config['CONRAID_REPO']
            conraid_repo_name: str = repos_config['CONRAID_REPO_NAME']
            conraid_repo_local = repos_config['CONRAID_REPO_LOCAL']
            conraid_repo_mirror = repos_config['CONRAID_REPO_MIRROR']
            conraid_repo_packages: str = repos_config['CONRAID_REPO_PACKAGES']
            conraid_repo_checksums: str = repos_config['CONRAID_REPO_CHECKSUMS']
            conraid_repo_changelog: str = repos_config['CONRAID_REPO_CHANGELOG']
            conraid_repo_tag: str = repos_config['CONRAID_REPO_TAG']
            try:
                if conraid_repo_local[0].startswith('file'):
                    conraid_repo_path: Path = Path(
                        ''.join(conraid_repo_local).replace('file:', '')
                    )
            except IndexError:
                conraid_repo_local = ['']

            slackonly_repo: bool = repos_config['SLACKONLY_REPO']
            slackonly_repo_name: str = repos_config['SLACKONLY_REPO_NAME']
            slackonly_repo_local = repos_config['SLACKONLY_REPO_LOCAL']
            slackonly_repo_mirror = repos_config['SLACKONLY_REPO_MIRROR']
            slackonly_repo_packages: str = repos_config['SLACKONLY_REPO_PACKAGES']
            slackonly_repo_checksums: str = repos_config['SLACKONLY_REPO_CHECKSUMS']
            slackonly_repo_changelog: str = repos_config['SLACKONLY_REPO_CHANGELOG']
            slackonly_repo_tag: str = repos_config['SLACKONLY_REPO_TAG']
            try:
                if slackonly_repo_local[0].startswith('file'):
                    slackonly_repo_path: Path = Path(
                        ''.join(slackonly_repo_local).replace('file:', '')
                    )
            except IndexError:
                slackonly_repo_local = ['']

            salixos_repo: bool = repos_config['SALIXOS_REPO']
            salixos_repo_name: str = repos_config['SALIXOS_REPO_NAME']
            salixos_repo_local = repos_config['SALIXOS_REPO_LOCAL']
            salixos_repo_mirror = repos_config['SALIXOS_REPO_MIRROR']
            salixos_repo_packages: str = repos_config['SALIXOS_REPO_PACKAGES']
            salixos_repo_checksums: str = repos_config['SALIXOS_REPO_CHECKSUMS']
            salixos_repo_changelog: str = repos_config['SALIXOS_REPO_CHANGELOG']
            salixos_repo_tag: str = repos_config['SALIXOS_REPO_TAG']
            try:
                if salixos_repo_local[0].startswith('file'):
                    salixos_repo_path: Path = Path(
                        ''.join(salixos_repo_local).replace('file:', '')
                    )
            except IndexError:
                salixos_repo_local = ['']

            salixos_extra_repo: bool = repos_config['SALIXOS_EXTRA_REPO']
            salixos_extra_repo_name: str = repos_config['SALIXOS_EXTRA_REPO_NAME']
            salixos_extra_repo_local = repos_config['SALIXOS_EXTRA_REPO_LOCAL']
            salixos_extra_repo_mirror = repos_config['SALIXOS_EXTRA_REPO_MIRROR']
            salixos_extra_repo_packages: str = repos_config['SALIXOS_EXTRA_REPO_PACKAGES']
            salixos_extra_repo_checksums: str = repos_config['SALIXOS_EXTRA_REPO_CHECKSUMS']
            salixos_extra_repo_changelog: str = repos_config['SALIXOS_EXTRA_REPO_CHANGELOG']
            salixos_extra_repo_tag: str = repos_config['SALIXOS_EXTRA_REPO_TAG']
            try:
                if salixos_extra_repo_local[0].startswith('file'):
                    salixos_extra_repo_path: Path = Path(
                        ''.join(salixos_extra_repo_local).replace('file:', '')
                    )
            except IndexError:
                salixos_extra_repo_local = ['']

            salixos_patches_repo: bool = repos_config['SALIXOS_PATCHES_REPO']
            salixos_patches_repo_name: str = repos_config['SALIXOS_PATCHES_REPO_NAME']
            salixos_patches_repo_local = repos_config['SALIXOS_PATCHES_REPO_LOCAL']
            salixos_patches_repo_mirror = repos_config['SALIXOS_PATCHES_REPO_MIRROR']
            salixos_patches_repo_packages: str = repos_config['SALIXOS_PATCHES_REPO_PACKAGES']
            salixos_patches_repo_checksums: str = repos_config['SALIXOS_PATCHES_REPO_CHECKSUMS']
            salixos_patches_repo_changelog: str = repos_config['SALIXOS_PATCHES_REPO_CHANGELOG']
            salixos_patches_repo_tag: str = repos_config['SALIXOS_PATCHES_REPO_TAG']
            try:
                if salixos_patches_repo_local[0].startswith('file'):
                    salixos_patches_repo_path: Path = Path(
                        ''.join(salixos_patches_repo_local).replace('file:', '')
                    )
            except IndexError:
                salixos_patches_repo_local = ['']

            slackel_repo: bool = repos_config['SLACKEL_REPO']
            slackel_repo_name: str = repos_config['SLACKEL_REPO_NAME']
            slackel_repo_local = repos_config['SLACKEL_REPO_LOCAL']
            slackel_repo_mirror = repos_config['SLACKEL_REPO_MIRROR']
            slackel_repo_packages: str = repos_config['SLACKEL_REPO_PACKAGES']
            slackel_repo_checksums: str = repos_config['SLACKEL_REPO_CHECKSUMS']
            slackel_repo_changelog: str = repos_config['SLACKEL_REPO_CHANGELOG']
            slackel_repo_tag: str = repos_config['SLACKEL_REPO_TAG']
            try:
                if slackel_repo_local[0].startswith('file'):
                    slackel_repo_path: Path = Path(
                        ''.join(slackel_repo_local).replace('file:', '')
                    )
            except IndexError:
                slackel_repo_local = ['']

            slint_repo: bool = repos_config['SLINT_REPO']
            slint_repo_name: str = repos_config['SLINT_REPO_NAME']
            slint_repo_local = repos_config['SLINT_REPO_LOCAL']
            slint_repo_mirror = repos_config['SLINT_REPO_MIRROR']
            slint_repo_packages: str = repos_config['SLINT_REPO_PACKAGES']
            slint_repo_checksums: str = repos_config['SLINT_REPO_CHECKSUMS']
            slint_repo_changelog: str = repos_config['SLINT_REPO_CHANGELOG']
            slint_repo_tag: str = repos_config['SLINT_REPO_TAG']
            try:
                if slint_repo_local[0].startswith('file'):
                    slint_repo_path: Path = Path(
                        ''.join(slint_repo_local).replace('file:', '')
                    )
            except IndexError:
                slint_repo_local = ['']

    except (tomli.TOMLDecodeError, KeyError) as error:
        errors.raise_toml_error_message(error, repositories_toml_file)

    # Dictionary of configurations of repositories.
    repositories = {
        sbo_repo_name: {
            'enable': sbo_repo,
            'path': sbo_repo_path,
            'mirror': sbo_repo_mirror,
            'slackbuilds_txt': sbo_repo_slackbuilds,
            'changelog_txt': sbo_repo_changelog,
            'patch_tag': sbo_repo_patch_tag,
            'repo_tag': sbo_repo_tag},

        ponce_repo_name: {
            'enable': ponce_repo,
            'path': ponce_repo_path,
            'mirror': ponce_repo_mirror,
            'slackbuilds_txt': ponce_repo_slackbuilds,
            'changelog_txt': ponce_repo_changelog,
            'patch_tag': ponce_repo_patch_tag,
            'repo_tag': ponce_repo_tag},

        slack_repo_name: {
            'enable': slack_repo,
            'path': slack_repo_path,
            'mirror': slack_repo_mirror,
            'packages_txt': slack_repo_packages,
            'checksums_txt': slack_repo_checksums,
            'changelog_txt': slack_repo_changelog,
            'repo_tag': slack_repo_tag},

        slack_extra_repo_name: {
            'enable': slack_extra_repo,
            'path': slack_extra_repo_path,
            'mirror': slack_extra_repo_mirror,
            'packages_txt': slack_extra_repo_packages,
            'checksums_txt': slack_extra_repo_checksums,
            'changelog_txt': slack_extra_repo_changelog,
            'repo_tag': slack_extra_repo_tag},

        slack_patches_repo_name: {
            'enable': slack_patches_repo,
            'path': slack_patches_repo_path,
            'mirror': slack_patches_repo_mirror,
            'packages_txt': slack_patches_repo_packages,
            'checksums_txt': slack_patches_repo_checksums,
            'changelog_txt': slack_patches_repo_changelog,
            'repo_tag': slack_patches_repo_tag},

        alien_repo_name: {
            'enable': alien_repo,
            'path': alien_repo_path,
            'mirror': alien_repo_mirror,
            'packages_txt': alien_repo_packages,
            'checksums_txt': alien_repo_checksums,
            'changelog_txt': alien_repo_changelog,
            'repo_tag': alien_repo_tag},

        multilib_repo_name: {
            'enable': multilib_repo,
            'path': multilib_repo_path,
            'mirror': multilib_repo_mirror,
            'packages_txt': multilib_repo_packages,
            'checksums_txt': multilib_repo_checksums,
            'changelog_txt': multilib_repo_changelog,
            'repo_tag': multilib_repo_tag},

        restricted_repo_name: {
            'enable': restricted_repo,
            'path': restricted_repo_path,
            'mirror': restricted_repo_mirror,
            'packages_txt': restricted_repo_packages,
            'checksums_txt': restricted_repo_checksums,
            'changelog_txt': restricted_repo_changelog,
            'repo_tag': restricted_repo_tag},

        gnome_repo_name: {
            'enable': gnome_repo,
            'path': gnome_repo_path,
            'mirror': gnome_repo_mirror,
            'packages_txt': gnome_repo_packages,
            'checksums_txt': gnome_repo_checksums,
            'changelog_txt': gnome_repo_changelog,
            'repo_tag': gnome_repo_tag},

        msb_repo_name: {
            'enable': msb_repo,
            'path': msb_repo_path,
            'mirror': msb_repo_mirror,
            'packages_txt': msb_repo_packages,
            'checksums_txt': msb_repo_checksums,
            'changelog_txt': msb_repo_changelog,
            'repo_tag': msb_repo_tag},

        csb_repo_name: {
            'enable': csb_repo,
            'path': csb_repo_path,
            'mirror': csb_repo_mirror,
            'packages_txt': csb_repo_packages,
            'checksums_txt': csb_repo_checksums,
            'changelog_txt': csb_repo_changelog,
            'repo_tag': csb_repo_tag},

        conraid_repo_name: {
            'enable': conraid_repo,
            'path': conraid_repo_path,
            'mirror': conraid_repo_mirror,
            'packages_txt': conraid_repo_packages,
            'checksums_txt': conraid_repo_checksums,
            'changelog_txt': conraid_repo_changelog,
            'repo_tag': conraid_repo_tag},

        slackonly_repo_name: {
            'enable': slackonly_repo,
            'path': slackonly_repo_path,
            'mirror': slackonly_repo_mirror,
            'packages_txt': slackonly_repo_packages,
            'checksums_txt': slackonly_repo_checksums,
            'changelog_txt': slackonly_repo_changelog,
            'repo_tag': slackonly_repo_tag},

        salixos_repo_name: {
            'enable': salixos_repo,
            'path': salixos_repo_path,
            'mirror': salixos_repo_mirror,
            'packages_txt': salixos_repo_packages,
            'checksums_txt': salixos_repo_checksums,
            'changelog_txt': salixos_repo_changelog,
            'repo_tag': salixos_repo_tag},

        salixos_extra_repo_name: {
            'enable': salixos_extra_repo,
            'path': salixos_extra_repo_path,
            'mirror': salixos_extra_repo_mirror,
            'packages_txt': salixos_extra_repo_packages,
            'checksums_txt': salixos_extra_repo_checksums,
            'changelog_txt': salixos_extra_repo_changelog,
            'repo_tag': slack_extra_repo_tag},

        salixos_patches_repo_name: {
            'enable': salixos_patches_repo,
            'path': salixos_patches_repo_path,
            'mirror': salixos_patches_repo_mirror,
            'packages_txt': salixos_patches_repo_packages,
            'checksums_txt': salixos_patches_repo_checksums,
            'changelog_txt': salixos_patches_repo_changelog,
            'repo_tag': salixos_patches_repo_tag},

        slackel_repo_name: {
            'enable': slackel_repo,
            'path': slackel_repo_path,
            'mirror': slackel_repo_mirror,
            'packages_txt': slackel_repo_packages,
            'checksums_txt': slackel_repo_checksums,
            'changelog_txt': slackel_repo_changelog,
            'repo_tag': slackel_repo_tag},

        slint_repo_name: {
            'enable': slint_repo,
            'path': slint_repo_path,
            'mirror': slint_repo_mirror,
            'packages_txt': slint_repo_packages,
            'checksums_txt': slint_repo_checksums,
            'changelog_txt': slint_repo_changelog,
            'repo_tag': slint_repo_tag}
    }

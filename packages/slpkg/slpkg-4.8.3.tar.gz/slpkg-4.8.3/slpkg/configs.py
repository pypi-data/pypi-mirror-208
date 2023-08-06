#!/usr/bin/python3
# -*- coding: utf-8 -*-

import tomli
import platform
from pathlib import Path
from dataclasses import dataclass

from slpkg.logging_config import LoggingConfig
from slpkg.toml_error_message import TomlErrors


@dataclass
class Configs:
    """ Default configurations. """
    errors = TomlErrors()

    prog_name: str = 'slpkg'
    os_arch: str = platform.machine()
    tmp_path: Path = Path('/tmp')
    tmp_slpkg: Path = Path(tmp_path, prog_name)
    build_path: Path = Path(tmp_path, prog_name, 'build')
    download_only_path: Path = Path(tmp_slpkg, '')
    lib_path: Path = Path('/var/lib', prog_name)
    etc_path: Path = Path('/etc', prog_name)
    db_path: Path = Path(lib_path, 'database')
    log_packages: Path = Path('/var', 'log', 'packages')

    database_name: str = f'database.{prog_name}'
    file_list_suffix: str = '.pkgs'
    installpkg: str = 'upgradepkg --install-new'
    reinstall: str = 'upgradepkg --reinstall'
    removepkg: str = 'removepkg'
    colors: bool = True
    dialog: bool = True
    downloader: str = 'wget'
    wget_options: str = '--c -q --progress=bar:force:noscroll --show-progress'
    curl_options: str = ''
    lftp_get_options: str = '-c get -e'
    lftp_mirror_options: str = '-c mirror --parallel=100 --only-newer'
    silent_mode: bool = True
    ascii_characters: bool = True
    ask_question: bool = True
    parallel_downloads: bool = False
    file_pattern: str = '*'
    spinning_bar: str = True
    progress_spinner: str = 'pixel'
    spinner_color: str = 'green'

    proxy_address: str = ''
    proxy_username: str = ''
    proxy_password: str = ''

    try:
        # Load user configuration.
        config_path_file = Path(etc_path, f'{prog_name}.toml')
        if config_path_file.exists():
            with open(config_path_file, 'rb') as conf:
                configs = tomli.load(conf)

        if configs:
            config = configs['CONFIGS']

            os_arch: str = config['OS_ARCH']
            download_only_path: Path = Path(config['DOWNLOAD_ONLY_PATH'])
            ask_question: bool = config['ASK_QUESTION']
            installpkg: str = config['INSTALLPKG']
            reinstall: str = config['REINSTALL']
            removepkg: str = config['REMOVEPKG']
            colors: bool = config['COLORS']
            dialog: str = config['DIALOG']
            downloader: str = config['DOWNLOADER']
            wget_options: str = config['WGET_OPTIONS']
            curl_options: str = config['CURL_OPTIONS']
            lftp_get_options: str = config['LFTP_GET_OPTIONS']
            lftp_mirror_options: str = config['LFTP_MIRROR_OPTIONS']
            silent_mode: bool = config['SILENT_MODE']
            ascii_characters: bool = config['ASCII_CHARACTERS']
            file_list_suffix: str = config['FILE_LIST_SUFFIX']
            parallel_downloads: bool = config['PARALLEL_DOWNLOADS']
            file_pattern_conf: str = config['FILE_PATTERN']
            spinning_bar: str = config['SPINNING_BAR']
            progress_spinner: str = config['PROGRESS_SPINNER']
            spinner_color: str = config['SPINNER_COLOR']
            proxy_address: str = config['PROXY_ADDRESS']
            proxy_username: str = config['PROXY_USERNAME']
            proxy_password: str = config['PROXY_PASSWORD']

    except (KeyError, tomli.TOMLDecodeError) as error:
        errors.raise_toml_error_message(error, toml_file='/etc/slpkg/slpkg.toml')

    blink: str = ''
    bold: str = ''
    red: str = ''
    bred: str = ''
    green: str = ''
    bgreen: str = ''
    yellow: str = ''
    byellow: str = ''
    cyan: str = ''
    blue: str = ''
    grey: str = ''
    violet: str = ''
    endc: str = ''

    if colors:
        blink: str = '\033[32;5m'
        bold: str = '\033[1m'
        red: str = '\x1b[91m'
        bred: str = f'{bold}{red}'
        green: str = '\x1b[32m'
        bgreen: str = f'{bold}{green}'
        yellow: str = '\x1b[93m'
        byellow: str = f'{bold}{yellow}'
        cyan: str = '\x1b[96m'
        blue: str = '\x1b[94m'
        grey: str = '\x1b[38;5;247m'
        violet: str = '\x1b[35m'
        endc: str = '\x1b[0m'

    # Creating the paths if not exists
    paths = [
        db_path,
        lib_path,
        etc_path,
        build_path,
        tmp_slpkg,
        download_only_path,
        LoggingConfig.log_path
    ]

    for path in paths:
        if not path.is_dir():
            path.mkdir(parents=True, exist_ok=True)

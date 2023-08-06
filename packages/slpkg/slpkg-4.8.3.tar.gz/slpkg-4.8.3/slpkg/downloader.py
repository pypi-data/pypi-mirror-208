#!/usr/bin/python3
# -*- coding: utf-8 -*-

import shutil
from typing import Union
from pathlib import Path
from multiprocessing import Process
from urllib.parse import unquote, urlparse

from slpkg.configs import Configs
from slpkg.utilities import Utilities
from slpkg.error_messages import Errors


class Downloader(Configs):

    def __init__(self, path: Union[str, Path], urls: list, flags: list):
        super(Configs, self).__init__()
        self.path: Path = path
        self.urls: list = urls
        self.flags: list = flags

        self.errors = Errors()
        self.utils = Utilities()

        self.filename = None
        self.downloader_command: str = str()
        self.downloader_tools: dict = {
            'wget': self.wget_downloader,
            'wget2': self.wget_downloader,
            'curl': self.curl_downloader,
            'lftp': self.lftp_downloader
        }
        self.option_for_parallel: bool = self.utils.is_option(
            ['-P', '--parallel'], flags)

    def download(self) -> None:
        """ Starting the processing for downloading. """
        process: list = []

        if self.parallel_downloads or self.option_for_parallel:
            for url in self.urls:
                p1 = Process(target=self.tools, args=(url,))
                process.append(p1)
                p1.start()

            for proc in process:
                proc.join()
        else:
            for url in self.urls:
                self.tools(url)

    def tools(self, url: str) -> None:
        path: str = urlparse(url).path
        self.filename: str = unquote(Path(path).name)

        if url.startswith('file'):
            self.copy_local_binary_file(url)
        else:
            try:
                self.downloader_tools[self.downloader](url)
            except KeyError:
                self.errors.raise_error_message(f"Downloader '{self.downloader}' not supported", exit_status=1)

            self.utils.process(self.downloader_command)
            self.check_if_downloaded(url)

    def copy_local_binary_file(self, url: str) -> None:
        try:
            shutil.copy2(Path(url.replace('file:', '')), self.tmp_slpkg)
            print(f"{self.byellow}Copying{self.endc}: {Path(url.replace('file:', ''))} -> {self.tmp_slpkg}")
        except FileNotFoundError as error:
            self.errors.raise_error_message(f'{error}', 1)

    def wget_downloader(self, url: str) -> None:
        self.downloader_command: str = f'{self.downloader} {self.wget_options} --directory-prefix={self.path} "{url}"'

    def curl_downloader(self, url: str) -> None:
        self.downloader_command: str = (f'{self.downloader} {self.curl_options} "{url}" '
                                        f'--output {self.path}/{self.filename}')

    def lftp_downloader(self, url: str) -> None:
        self.downloader_command: str = f'{self.downloader} {self.lftp_get_options} {url} -o {self.path}'

    def check_if_downloaded(self, url: str) -> None:
        path_file: Path = Path(self.path, self.filename)
        if not path_file.exists():
            self.errors.raise_error_message(f"Download the '{url}'", exit_status=20)

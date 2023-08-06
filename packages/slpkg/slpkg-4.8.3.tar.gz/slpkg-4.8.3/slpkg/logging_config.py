#!/usr/bin/python3
# -*- coding: utf-8 -*-

import logging
from pathlib import Path
from datetime import datetime


class LoggingConfig:
    date_now = datetime.now()
    level = logging.INFO
    filemode: str = 'w'
    encoding: str = 'utf-8'
    log_path: Path = Path('/tmp/slpkg/logs')
    log_file: Path = Path(log_path, 'slpkg.log')
    date: str = f'{date_now.day}/{date_now.month}/{date_now.year}'
    time: str = f'{date_now.hour}:{date_now.minute}:{date_now.second}'
    date_time: str = f'{date} {time}'

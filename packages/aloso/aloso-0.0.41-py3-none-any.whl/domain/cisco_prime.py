import ftplib
import logging
from dataclasses import dataclass
from ftplib import FTP
from typing import ClassVar

import config

logging.basicConfig(level=config.debug_level,
                    format='%(asctime)s %(levelname)s %(pathname)s %(funcName)s %(lineno)d : %(message)s',
                    datefmt='%d/%m/%Y %H:%M:%S',
                    filename=config.logs_file_path,
                    filemode='a')


@dataclass
class CiscoPrime:
    name: str = ""
    ip: str = ""
    port: str = ""
    password: str = ""

    @staticmethod
    def get_all_devices():
        pass

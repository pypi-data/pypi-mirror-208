import logging
from dataclasses import dataclass

import config

logging.basicConfig(level=config.debug_level,
                    format='%(asctime)s %(levelname)s %(pathname)s %(funcName)s %(lineno)d : %(message)s',
                    datefmt='%d/%m/%Y %H:%M:%S',
                    filename=config.logs_file_path,
                    filemode='a')


@dataclass
class Certificate:
    country: str = ""
    state: str = ""
    locality: str = ""
    organization: str = ""
    unit: str = ""
    common: str = ""
    mail: str = ""

    def renew(self):
        pass

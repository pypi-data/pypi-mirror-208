import logging
from dataclasses import dataclass, field
from typing import List

import config

logging.basicConfig(level=config.debug_level,
                    format='%(asctime)s %(levelname)s %(pathname)s %(funcName)s %(lineno)d : %(message)s',
                    datefmt='%d/%m/%Y %H:%M:%S',
                    filename=config.logs_file_path,
                    filemode='a')


@dataclass
class Alias:
    name: str = ""
    open_data: List[str] = field(default_factory=list)

    def get_records(self, alias_file_path: str):
        pass

    def alias_is_available(self):
        return self.name not in self.open_data and len(self.name) > 2

    def create_alias(self, server_ip: str, alias_file_path: str):
        pass

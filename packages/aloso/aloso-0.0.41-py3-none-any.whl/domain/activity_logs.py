import logging
from dataclasses import dataclass
from datetime import time

import config

logging.basicConfig(level=config.debug_level,
                    format='%(asctime)s %(levelname)s %(pathname)s %(funcName)s %(lineno)d : %(message)s',
                    datefmt='%d/%m/%Y %H:%M:%S',
                    filename=config.logs_file_path,
                    filemode='a')


@dataclass
class ActivityLogs:
    timesstamp: str
    author: str
    action: str

    @staticmethod
    def get_all_activity_logs():
        pass

    def create_activity_log(self):
        pass

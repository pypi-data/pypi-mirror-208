import logging
from dataclasses import dataclass

import config

logging.basicConfig(level=config.debug_level,
                    format='%(asctime)s %(levelname)s %(pathname)s %(funcName)s %(lineno)d : %(message)s',
                    datefmt='%d/%m/%Y %H:%M:%S',
                    filename=config.logs_file_path,
                    filemode='a')


@dataclass
class Grafana:
    @staticmethod
    def install_grafana():
        pass

    @staticmethod
    def install_loki():
        pass

    @staticmethod
    def install_promtail():
        pass

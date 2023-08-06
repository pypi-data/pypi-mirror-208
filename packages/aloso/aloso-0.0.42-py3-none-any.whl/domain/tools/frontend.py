import logging
from dataclasses import dataclass

import config

logging.basicConfig(level=config.debug_level,
                    format='%(asctime)s %(levelname)s %(pathname)s %(funcName)s %(lineno)d : %(message)s',
                    datefmt='%d/%m/%Y %H:%M:%S',
                    filename=config.logs_file_path,
                    filemode='a')


@dataclass
class Frontend:

    @staticmethod
    def install_nodejs() -> None:
        pass

    @staticmethod
    def install_nginx(app_name: str = config.application_name) -> None:
        pass

    @staticmethod
    def generate_app(app_name: str = config.application_name) -> None:
        pass

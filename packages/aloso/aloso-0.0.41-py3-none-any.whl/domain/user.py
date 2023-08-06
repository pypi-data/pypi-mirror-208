import logging
from dataclasses import dataclass

import config

logging.basicConfig(level=config.debug_level,
                    format='%(asctime)s %(levelname)s %(pathname)s %(funcName)s %(lineno)d : %(message)s',
                    datefmt='%d/%m/%Y %H:%M:%S',
                    filename=config.logs_file_path,
                    filemode='a')


@dataclass
class User:
    id: int
    username: str = ""
    password: str = ""
    admin: bool = False
    change_pwd: bool = False

    def create(self):
        pass

    def update(self):
        pass

    @staticmethod
    def get_user_by_id(id_user):
        pass

    @staticmethod
    def get_user_by_name(name_user):
        pass

    def hash_pass(self):
        pass

    def user_check(self):
        pass
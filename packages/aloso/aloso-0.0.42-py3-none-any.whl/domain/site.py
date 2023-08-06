import logging
from dataclasses import dataclass

import config

logging.basicConfig(level=config.debug_level,
                    format='%(asctime)s %(levelname)s %(pathname)s %(funcName)s %(lineno)d : %(message)s',
                    datefmt='%d/%m/%Y %H:%M:%S',
                    filename=config.logs_file_path,
                    filemode='a')


@dataclass
class Site:
    site_name: str

    #    contacts: list[Contact]

    @staticmethod
    def get_all():
        pass

    @staticmethod
    def get_site_by_id(id_site):
        pass

    def get_contacts_by_site_id(self):
        pass

    def create(self):
        pass

    def update(self):
        pass

    def delete(self):
        pass

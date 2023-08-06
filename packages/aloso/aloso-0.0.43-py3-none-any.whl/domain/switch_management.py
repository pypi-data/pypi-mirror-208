from dataclasses import dataclass
from datetime import datetime

from domain.equipment_management import Equipments
import config
import logging

logging.basicConfig(level=config.debug_level,
                    format='%(asctime)s %(levelname)s %(pathname)s %(funcName)s %(lineno)d : %(message)s',
                    datefmt='%d/%m/%Y %H:%M:%S',
                    filename=config.logs_file_path,
                    filemode='a')


@dataclass
class TypeSwitch:
    name: str = ""


@dataclass
class Switch(Equipments):
    date: datetime = datetime.now()
    config: str = ''
    switch_type: TypeSwitch = TypeSwitch()

    @staticmethod
    def save_config(switch_config_file):
        pass

    @staticmethod
    def get_inventory_file():
        pass

    def get_config(self, switch_name):
        pass

    @staticmethod
    def save_configs_all_switches():
        pass

    def load_all_switches_configs(self):
        pass

    def new_name_config_file(self):
        pass

    @staticmethod
    def versioning_configs_from_ftp():
        pass

    @staticmethod
    def save_configs_auto(hour: str):
        pass

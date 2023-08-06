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
class TypeEquipments:
    name: str = ""


@dataclass
class Equipments:
    building_id: int = 0
    id_group: int = 0
    id: int = 0
    name: str = ""
    ip: str = ""
    mac: str = ""
    equipment_type: TypeEquipments = TypeEquipments()
    equipment_dict: ClassVar[dict] = {}
    version: str = ""

    @staticmethod
    def check_ftp_connection(username: str,
                             password: str,
                             host: str):
        pass

    @staticmethod
    def ssh_open_connection(equipment_name):
        pass

    @staticmethod
    def load_all(file_path: str):
        pass

    @staticmethod
    def ftp_get_config_files():
        pass

    @staticmethod
    def new_name_file_from_ftp_dir(file_name: str):
        pass

    @staticmethod
    def get_date_from_ftp_file(file_name: str):
        pass

    @staticmethod
    def recent_date_detection(ftp: FTP):
        pass

    def server_exists(self):
        pass

    @staticmethod
    def get_equipments_version(file_path: str):
        pass

    @staticmethod
    def version_alert(actual_version: str, new_version: str):
        pass

    @staticmethod
    def get_most_recent_file_info(directory_path: str, connection: ftplib.FTP) -> dict[str, any]:
        pass

    @staticmethod
    def was_updated_recently(last_modification_date: str, frequency: int) -> bool:
        pass

    @staticmethod
    def get_equipments_directories_files_date_and_size() -> dict:
        pass

    @staticmethod
    def get_equipment_version(command: str):
        pass

    @staticmethod
    def get_all_equipments_versions(command: list):
        pass

import configparser
import ftplib
import logging
import random
import socket
from datetime import datetime
from ftplib import FTP

import fabric
from fabric import Connection, Config

import config
from domain.equipment_management import Equipments
from output.models.equipments_directories_database import EquipmentsDirectoriesData
from output.shell.configs_shell import ConfigsShell


class EquipmentShell(Equipments):

    @staticmethod
    def check_ftp_connection(username: str = config.ftp_username,
                             password: str = ConfigsShell.get_value('ftp_password'),
                             host: str = config.ftp_host):
        is_connected: bool = False
        try:
            assert socket.gethostbyname(host) == host
            ftp = FTP(host=host, user=username, passwd=password, timeout=5)
            ftp.quit()
            is_connected = True
        except Exception as e:
            logging.error(e)
        finally:
            return is_connected

    @staticmethod
    def ssh_open_connection(equipment_name):
        # Test done
        try:
            connection = fabric.Connection(equipment_name, user=config.ssh_username, port=config.equipments_port,
                                           connect_kwargs={'password': ConfigsShell.get_value('equipments_password')},
                                           connect_timeout=5)
            connection.open()
            return connection
        except Exception as e:
            logging.error(e)

    @staticmethod
    def load_all(file_path: str = f"{config.inventory_local_directory}/{config.inventory_file_name}"):
        # Test done
        try:
            config_ = configparser.ConfigParser(allow_no_value=True)
            config_.read(file_path)

            equipments_dict: dict = {}

            for section in config_.sections():
                for variable in config_[section]:
                    if variable.__contains__(config.separateur):
                        equipment = EquipmentShell()
                        equipment.name = variable.split(config.separateur)[0]
                        equipment.ip = variable.split(config.separateur)[1].removesuffix("\n")
                        # TODO: Fake versions
                        equipment.version = equipment.get_equipment_version()
                        # EquipmentShell.equipment_list.append(equipment)
                        equipments_dict[section] = equipments_dict.get(section, []) + [equipment]
            EquipmentShell.equipment_dict = equipments_dict
            return equipments_dict
        except Exception as e:
            logging.error(e)

    @staticmethod
    def ftp_get_config_files(dir_ftp_switchs: str = config.directory_ftp_switchs):
        # Tests done
        try:
            ftp_host = config.ftp_host
            ftp_user = config.ftp_username
            ftp_directory = config.directory_ftp_switchs

            logging.info(f"FTP connection : host = {ftp_host}, user = {ftp_user}, directory = {ftp_directory}")
            ftp = FTP(host=ftp_host, user=ftp_user, passwd=ConfigsShell.get_value('ftp_password'))
            ftp.cwd(dir_ftp_switchs)

            files_in_ftp_dir = ftp.nlst()

            date_limit = EquipmentShell.recent_date_detection(ftp)
            logging.info(f"Most recent date : {date_limit} in directory {ftp_directory}")

            for file in files_in_ftp_dir:
                date_file = EquipmentShell.get_date_from_ftp_file(file)
                if date_file == date_limit:
                    ftp.retrbinary(f"RETR {file}", open(
                        f"{config.switch_configs_local_directory}/{EquipmentShell.new_name_file_from_ftp_dir(file)}",
                        'wb').write)
                    # logging.info(f"File {file}_{date_file} downloaded from FTP")
            logging.info("Configs versioning done!")
        except Exception as e:
            logging.error(e)

    @staticmethod
    def create(name_group: str, list_values: list,
               file_path: str = f"{config.inventory_local_directory}/{config.inventory_file_name}"):
        try:
            config_ = configparser.ConfigParser(allow_no_value=True)
            config_.read(file_path)

            config_.add_section(name_group)

            for ligne in list_values:
                if len(ligne.split(' ')) >= 3:
                    return False
                name = ligne.split(' ')[0]
                ip = ligne.split(' ')[1]
                # version = 'v1.0'  # ligne.split(' ')[2]
                config_.set(name_group, f"{name}{config.separateur}{ip}", None)

            with open(file_path, 'w') as configfile:
                config_.write(configfile)
                logging.info(f"Equipment {name_group} created")
            return True
        except Exception as e:
            logging.error(e)
            return False

    @staticmethod
    def edit(name_group: str, list_values: list,
             file_path: str = f"{config.inventory_local_directory}/{config.inventory_file_name}"):
        try:

            config_ = configparser.ConfigParser(allow_no_value=True)
            config_.read(file_path)

            for section in config_.sections():
                if section == name_group:
                    config_.remove_section(name_group)
                    config_.add_section(name_group)

            for ligne in list_values:
                if len(ligne.split(' ')) >= 3:
                    return False
                name = ligne.split(' ')[0]
                ip = ligne.split(' ')[1]
                # version = 'v1.0'  # ligne.split(' ')[2]
                config_.set(name_group, f"{name}{config.separateur}{ip}", None)

            with open(file_path, 'w') as configfile_edit:
                config_.write(configfile_edit)
            logging.info(f"Equipment {name_group} edited")
            return True
        except Exception as e:
            logging.error(e)
            return e.__str__()

    @staticmethod
    def remove(name_group: str,
               file_path: str = f"{config.inventory_local_directory}/{config.inventory_file_name}"):
        try:
            config_ = configparser.ConfigParser(allow_no_value=True)
            config_.read(file_path)

            for section in config_.sections():
                if section == name_group:
                    config_.remove_section(name_group)

            with open(file_path, 'w') as configfile_remove:
                config_.write(configfile_remove)
            logging.info(f"Equipment {name_group} remove")
            return True
        except Exception as e:
            logging.error(e)
            return e.__str__()

    @staticmethod
    def check_ssh_connection(username, host,port, equipment_group) -> bool:
        is_connected: bool = False
        try:
            assert socket.gethostbyname(host) == host
            conn = Connection(host=host,
                              config=Config(overrides={'user': username, 'port': port}),
                              connect_kwargs={'password': ConfigsShell.get_value('equipments_password')},
                              connect_timeout=5)
            conn.open()
            conn.close()
            is_connected = True
        except AssertionError as ae:
            logging.error(f"Erreur de connexion au serveur : {username} ({host}) dans {equipment_group} {ae}")
        except TimeoutError as te:
            logging.error(f"Erreur de connexion au serveur : {username} ({host}) dans {equipment_group} {te}")
        except Exception as e:
            logging.error(f"Erreur de connexion au serveur : {e}")
        finally:
            return is_connected

    @staticmethod
    def new_name_file_from_ftp_dir(file_name: str):
        # Tests done
        try:
            return f"{file_name.split('_')[0]}.txt"
        except Exception as e:
            logging.error(e)

    @staticmethod
    def get_date_from_ftp_file(file_name: str):
        # Tests done
        try:
            return f"{file_name.split('_')[1].split('.')[0]}"
        except Exception as e:
            logging.error(e)

    @staticmethod
    def recent_date_detection(ftp: FTP):
        # Tests done
        try:
            files_in_ftp_dir = ftp.nlst()

            older_date = datetime.min.strftime('%Y%m%d')

            for file in files_in_ftp_dir:
                date_file = EquipmentShell.get_date_from_ftp_file(file)
                if date_file > older_date:
                    older_date = date_file
            return older_date
        except Exception as e:
            logging.error(e)

    def server_exists(self):
        # TODO récuperation liste des serveurs
        servers = ["serv1", "serv2", "serv3"]
        return self.name in servers

    @staticmethod
    def get_equipments_version(file_path: str):
        equipments_version = {}
        for keys, values in EquipmentShell.load_all(file_path=file_path).items():
            for equipment in values:
                equipments_version[equipment.name] = equipment.version
        return equipments_version

    @staticmethod
    def version_alert(actual_version: str, new_version: str):
        equipments_actual_version = EquipmentShell.get_equipments_version(file_path=actual_version)
        equipments_new_version = EquipmentShell.get_equipments_version(file_path=new_version)
        equipments_diff = {}

        for aKeys, aValues, nKeys, nValues in zip(equipments_actual_version.keys(), equipments_actual_version.values(),
                                                  equipments_new_version.keys(), equipments_new_version.values()):
            if aValues != nValues:
                equipments_diff[aKeys] = nValues
        return equipments_diff

    @staticmethod
    # Tested and mocked
    def get_most_recent_file_info(directory_path: str, connection: ftplib.FTP) -> dict[str, any]:
        result = {"file": "", "modification_date": datetime.min, "file_size": 0}
        try:
            connection.cwd(directory_path)
            files = connection.nlst()
            if not files:
                return result
            recent_file = max(files, key=lambda x: x.split('_')[0])
            file_size = int(connection.size(recent_file))
            recent_date = datetime.strptime(recent_file.split('_')[0], "%Y%m%d").strftime("%Y-%m-%d")
            result = {"file": recent_file, "modification_date": recent_date, "file_size": file_size}
        except Exception as e:
            logging.error(f"Erreur lors de la récupération du fichier le plus récent de {directory_path} : {e}")
        finally:
            return result

    @staticmethod
    # Tested and mocked
    def was_updated_recently(last_modification_date: str, frequency: int) -> bool:
        result = False
        try:
            difference = datetime.now() - datetime.strptime(last_modification_date, "%Y-%m-%d")
            if difference.days <= frequency:
                result = True
        except Exception as e:
            logging.error(f"Erreur lors de la vérification de la fréquence de mise à jour : {e}")
        finally:
            return result

    @staticmethod
    def get_equipments_directories_files_date_and_size() -> dict:
        parent_directory = config.equipement_ftp_remote_directory
        sub_directories = [(value.get("name"), value.get("frequency")) for key, value in
                           EquipmentsDirectoriesData.get_all().items()]
        content = {}
        try:
            with ftplib.FTP() as connection:
                connection.connect(host=config.ftp_host)
                connection.login(user=config.ftp_username, passwd=ConfigsShell.get_value("ftp_password"))
                for sub_directory in sub_directories:
                    sub_path = f"{parent_directory}/{sub_directory[0]}"
                    content[sub_directory[0]] = EquipmentShell.get_most_recent_file_info(directory_path=sub_path,
                                                                                         connection=connection)
                    content[sub_directory[0]]["updated_recently"] = EquipmentShell.was_updated_recently(
                        last_modification_date=content[sub_directory[0]]["modification_date"],
                        frequency=sub_directory[1])
        except Exception as e:
            logging.error(f"Erreur lors de la récupération des informations des fichiers : {e}")

        finally:
            return content

    # Tested and mocked
    def get_equipment_version(self, command: str = None):
        sub_command = "sh version | i version" if command is None else command
        username = config.ssh_equipment_username
        port = config.ssh_equipment_port
        password = config.ssh_equipment_password

        # try:
        #     with Connection(host=self.ip, connect_kwargs={"password": password}, user=username, port=port) as c:
        #
        #         result = c.run(sub_command, hide=True)
        #         if result.exited != 0:
        #             logging.error(f"Erreur lors de la récupération de la version de l'équipement : {result.stderr}")
        #             raise Exception(result.stderr)
        #         return result.stdout.split(", Version ")[1].split(", ")[0]
        # except Exception as e:
        #     logging.error(f"Erreur lors de la récupération de la version de l'équipement : {e}")
        #     raise Exception(e)

        try:
            number: float = random.uniform(0.1, 3.0)
            return f"v{number:.2f}"
        except Exception as e:
            logging.error(e)

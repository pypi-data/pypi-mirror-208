import curses
import os
import tempfile
import time
from datetime import datetime
import logging

import schedule

import config
from domain.switch_management import Switch
from output.shell.equipment_shell import EquipmentShell


class SwitchShell(Switch):

    def get_inventory_file(self):
        # Test done
        local_directory = config.inventory_local_directory
        inventory_name = config.inventory_file_name
        temp = tempfile.mkdtemp()

        try:
            os.system(
                # f"git clone https://{username}:{password}@{pull_repo} {temp} ;" with token
                f"git clone {config.repository_to_load_inventory_with_ssh} {temp};"
                f"cp {temp}/{inventory_name} {local_directory} ;"
                f"rm -r {temp}")
            logging.info(f"Récupération de l'inventaire depuis le depot git")
        except Exception as e:
            logging.error(f"Erreur lors de la récupération de l'inventaire : {e}")

    @staticmethod
    def save_config(switch_config_file: str):
        # Test skipped
        temp = tempfile.mkdtemp()

        file = switch_config_file.split("/")[-1]

        try:
            # os.system(f"git clone https://{username}:{password}@{push_repo} {temp}") with token
            os.system(f"git clone {config.repository_to_save_configs_for_all_switches_with_ssh} {temp}")
            logging.info(f"Récupération du dépôt de sauvegarde effectuée")

            os.system(
                f"cd {temp} ; "
                "git init ;"
                f"cp {config.switch_configs_local_directory}/* {temp} ;"
                f"git add . ;"
                f"git commit -m 'Switch Configuration File {datetime.now().strftime('%d-%m-%y | %H:%M')}' ;"
                "git push ; "
                f"rm -rf {temp}")
            logging.info(f"Envoi de la configuration du switch {file} vers le dépôt de sauvegarde effectuée")
        except Exception as e:
            logging.error(
                f"Erreur lors de l'envoi de la configuration du switch {file} vers le dépôt de sauvegarde : {e}")

    """# With FTP
    def get_config(self, switch_name):
        # Test done
        connection = EquipmentShell.ssh_open_connection(switch_name)
        connection.get(f"{config.ssh_directory_config_path}/{config.ssh_config_file_name}",
                       f"{config.switch_configs_local_directory}/{self.new_name_config_file()}")
        # os.system(f"{self.sftp_get_command(switch_name)}")"""

    @staticmethod
    def save_configs_all_switches():
        # Test skipped
        try:
            logging.info(
                f"Nombre de fichiers de configuration de switchs :: {len(os.listdir(config.switch_configs_local_directory))}")
            # for file in os.scandir(config.switch_configs_local_directory):
            SwitchShell.save_config(config.switch_configs_local_directory)
            logging.info(
                f"Les fichiers de configuration {config.switch_configs_local_directory} ont été sauvegardés sur le dépôt de sauvegarde")
        except Exception as e:
            logging.error(f"Erreur lors de la sauvegarde des configurations des switchs :: {e}")

    def load_all_switches_configs(self):
        # Test skipped
        EquipmentShell.load_all()
        for switch_equipment in EquipmentShell.equipment_dict['Switchs']:
            self.name = switch_equipment.name
            self.get_config(switch_equipment.ip)

    @staticmethod
    def save_configs_auto(hour: str = config.saving_hour):
        schedule.every().day.at(hour).do(SwitchShell.save_configs_all_switches)
        curses.initscr().nodelay(True)
        while True:
            schedule.run_pending()
            time.sleep(1)
            try:
                logging.info(f"Sauvegarde automatique des configurations des switchs")
                ch = curses.initscr().getch()
                if ch == ord('q'):
                    curses.beep()
                    exit(0)
            except KeyboardInterrupt:
                logging.info(f"Fin de la sauvegarde automatique des configurations des switchs")
                return

    @staticmethod
    def versioning_configs_from_ftp():
        try:
            EquipmentShell.ftp_get_config_files()
            SwitchShell.save_configs_all_switches()
            return True
        except Exception as e:
            logging.error(f"Erreur lors de la sauvegarde des configurations des switchs :: {e}")
            return False

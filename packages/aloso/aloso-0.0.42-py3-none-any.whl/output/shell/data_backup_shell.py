import logging
import os
import shutil
import socket
import time
import zipfile
from datetime import datetime
from typing import Optional

import schedule

import config
from domain.data_backup import Backup
from output.shell.shell import Shell


class BackupShell(Backup):

    @staticmethod
    def check_ssh_connection(username: str = config.backup_username, host: str = config.backup_host,
                             port: int = config.backup_port) -> bool:
        is_connected: bool = False

        try:
            socket.inet_aton(host)
            with Shell.ssh_connection(host=host, username=username, port=port) as con:
                con.open()
                is_connected = True
                logging.info(f"Connexion SSH réussie au serveur {host}")
        except Exception as e:
            logging.error(f"Erreur de connexion SSH au serveur {host} : {e}")

        return is_connected

    @staticmethod
    def backup(host: str = config.backup_host, username: str = config.backup_username,
               port: int = config.backup_port, password: Optional[str] = None) -> None:
        date: str = datetime.now().strftime('%Y%m%d_%H%M%S')

        source_dir: str = config.root_dir
        config_file: str = config.config_file
        destination_dir: str = config.backup_target_dir

        try:
            shutil.make_archive(base_name=date, format='zip', root_dir=source_dir, base_dir="data")

            with zipfile.ZipFile(f"{date}.zip", 'a') as zip_file:
                zip_file.write(config_file, os.path.basename(config_file))

            with Shell.ssh_connection(host=host, username=username,
                                      port=port, password=password) as conn:
                conn.put(f"{date}.zip", f"{destination_dir}/{date}.zip")

            os.remove(f"{date}.zip")

            logging.info(f"Backup effectué avec succès dans {destination_dir}")
        except Exception as e:
            logging.error(f"Erreur de backup : {e}")

    @staticmethod
    def schedule_backup(host: str = config.backup_host, username: str = config.backup_username,
                        port: int = config.backup_port, password: Optional[str] = None) -> None:
        schedule.every().day.at(config.backup_hour).do(BackupShell.backup, host=host, username=username, port=port,
                                                       password=password)
        while True:
            schedule.run_pending()
            time.sleep(1)

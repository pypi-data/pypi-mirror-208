import logging

from fabric import Connection, Config

import config
from domain.tools.ansible import Ansible


class AnsibleShell(Ansible):

    @staticmethod
    def connection():
        configuration = Config(overrides={'user': config.ansible_username,
                                          'port': config.ansible_port,
                                          'sudo': {'password': config.ansible_password}})
        try:
            conn = Connection(host=config.ansible_host, config=configuration)
            return conn
        except Exception as e:
            logging.error(f"Erreur de connexion au serveur : {e}")

    @staticmethod
    def install_ansible():
        conn = AnsibleShell.connection()

        commands = [
            'apt update -y',
            "sudo apt install software-properties-common -y",
            "sudo add-apt-repository --yes --update ppa:ansible/ansible -y",
            "sudo apt install ansible -y"]

        for command in commands:
            try:
                if config.use_sudo:
                    conn.sudo(command)
                else:
                    conn.run(command)
            except Exception as e:
                logging.error(f"Erreur d'installation d'ansible : {e}")

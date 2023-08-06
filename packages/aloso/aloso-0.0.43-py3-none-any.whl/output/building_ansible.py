import logging

import config
from domain.building import Building
from output.shell.shell import Shell


class BuildingAnsible(Building):

    def execute(self, *args):
        conn = Shell.ssh_connection(host=config.ansible_host,
                                    username=config.ansible_username,
                                    password=config.ansible_password,
                                    port=config.ansible_port)
        inventory = args[0]
        playbook = args[1]
        self.name = args[2]

        cmd = f"ansible-playbook -i {inventory} {playbook} -e building='{self.name}'"

        try:
            with conn:
                conn.run(cmd)
            logging.info(f"Playbook {playbook} executé avec succès sur le batiment {self.name}")
        except Exception as e:
            logging.error(f"Erreur d'execution du playbook : {e} sur le batiment {self.name}")

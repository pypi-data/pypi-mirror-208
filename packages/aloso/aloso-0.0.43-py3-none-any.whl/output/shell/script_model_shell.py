import configparser
import logging
import os
from datetime import datetime

import config
from domain.script_model import ScriptModel
from output.shell.equipment_shell import EquipmentShell


class ScriptModelShell(ScriptModel):

    def exec_commands_on_equipments(self, file_name: str, list_equipments: list,
                                    directory: str = config.templates_directory_path):
        # Test done
        commands_exec, variables_exec = self.recuperation_data_ini_file(file_name, directory)
        logging.info(f"Récupération des commandes et des variables effectuée")

        logging.info(f"Nombres d'équipements à traiter : {len(list_equipments)}")
        try:
            for equipment in list_equipments:
                connection = EquipmentShell.ssh_open_connection(equipment.ip)
                if connection.is_connected:
                    connection.run(self.load_command_with_variables(commands_exec, variables_exec))
                    connection.close()
                    logging.info(f"Exécution des commandes sur l'équipement {equipment.name} effectuée")
                else:
                    logging.error(f"Erreur lors de l'exécution des commandes sur l'équipement {equipment.name}")
            return True
        except Exception as err:
            logging.error(f"Une erreur est survenu lors de l'exécution {err.__str__()}")
            return False

    @staticmethod
    def modify_template_before_execution(file_name: str, command_template: list, variables_template: dict,
                                         directory: str = config.templates_directory_path):
        # Test done
        with open(f"{directory}/{file_name}.ini", 'w') as prov_file:
            prov_file.write("[variables]\n")
            for variable_line in variables_template:
                prov_file.write(f"{variable_line} = {variables_template[variable_line]}\n")

            prov_file.write(f"\n[command]\ncommands = ")
            for command_line in command_template:
                prov_file.write(f"{command_line}\n\t")

    @staticmethod
    def recuperation_data_ini_file(filename: str, template_directory_path: str = config.templates_directory_path):
        # Test done
        filepath = f"{template_directory_path}/{filename}.ini"
        config_ = configparser.ConfigParser()
        config_.read(filepath)

        commands_template = " ; ".join(config_['command']['commands'].split("\n"))
        variables_template: dict = {}

        for section in config_.sections():
            if section == "variables":
                for variable in config_[section]:
                    variables_template[variable] = config_[section][variable]

        return commands_template, variables_template

    @staticmethod
    def load_command_with_variables(config_command: str, config_variables: dict):
        # Test done
        return config_command.format(**config_variables)

    @staticmethod
    def get_list_of_templates_names(templates_directory: str):
        # Test done
        try:
            return [file.name.removesuffix(".ini") for file in os.scandir(templates_directory) if
                file.name.endswith(".ini")]
        except Exception as e:
            logging.error(f"Erreur lors de la récupération des noms de template : {e}")
            return []

    @staticmethod
    def get_all_templates_content(templates_directory: str):
        # Test done
        templates_content = {}
        for template_name in ScriptModelShell.get_list_of_templates_names(templates_directory):
            templates_content[template_name] = ScriptModelShell.get_template_content(template_name, templates_directory)
        return templates_content

    @staticmethod
    def get_template_content(template_name: str, templates_directory: str):
        # Test done
        template_content = {"variables": {}, "commands": []}
        command_prov, variables_prov = ScriptModelShell.recuperation_data_ini_file(template_name, templates_directory)
        template_content["commands"] = command_prov.split(" ; ")
        template_content["variables"] = variables_prov
        return template_content

    @staticmethod
    def create_provisioning_templates(file_type, command_template: list, variables_template: dict):
        # Test done
        file_name = f"{file_type}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        logging.info(f"Création du fichier de template de provisionning {file_name}")

        with open(f"{config.templates_directory_path}/{file_name}.ini", 'w') as prov_file:
            prov_file.write("[variables]\n")
            for variable_line in variables_template:
                prov_file.write(f"{variable_line} = {variables_template[variable_line]}\n")
            logging.info(f"Variables ajoutées au fichier de template de provisionning {file_name}")

            prov_file.write(f"\n[command]\ncommands = ")
            for command_line in command_template:
                prov_file.write(f"{command_line}\n\t")
            logging.info(f"Commandes ajoutées au fichier de template de provisionning {file_name}")

    @staticmethod
    def remove_template(file_name, date: str, directory: str = config.templates_directory_path):
        # Test done
        try:
            os.remove(f"{directory}/{file_name}_{date}.ini")
            logging.info(f"Suppression du fichier de template de provisionning {file_name}_{date} effectuée")
            return 0
        except FileNotFoundError:
            logging.error(f"Le fichier de template de provisionning {file_name}_{date} n'existe pas")
            return 1

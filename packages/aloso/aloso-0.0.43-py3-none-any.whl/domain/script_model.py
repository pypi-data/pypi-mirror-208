import logging
from dataclasses import dataclass

import config

logging.basicConfig(level=config.debug_level,
                    format='%(asctime)s %(levelname)s %(pathname)s %(funcName)s %(lineno)d : %(message)s',
                    datefmt='%d/%m/%Y %H:%M:%S',
                    filename=config.logs_file_path,
                    filemode='a')


@dataclass
class ScriptModel:

    def exec_commands_on_equipments(self, file_name: str, list_equipments: list,
                                    directory: str = config.templates_directory_path):
        pass

    @staticmethod
    def modify_template_before_execution(file_name: str, command_template: list, variables_template: dict,
                                         directory: str = config.templates_directory_path):
        pass

    @staticmethod
    def recuperation_data_ini_file(filename: str, template_directory_path: str = config.templates_directory_path):
        pass

    @staticmethod
    def load_command_with_variables(config_command: str, config_variables: dict):
        pass

    @staticmethod
    def create_provisioning_templates(file_type, command_template: list, variables_template: dict):
        pass

    @staticmethod
    def remove_template(file_name, date: str, directory: str = config.templates_directory_path):
        pass

    @staticmethod
    def get_list_of_templates_names(templates_directory: str):
        pass

    @staticmethod
    def get_all_templates_content(templates_directory: str):
        pass

    @staticmethod
    def get_template_content(template_name: str, templates_directory: str):
        pass

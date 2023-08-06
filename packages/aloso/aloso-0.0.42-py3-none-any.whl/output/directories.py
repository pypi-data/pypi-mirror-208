import os

import config


def create_directory(directory: str):
    if not os.path.exists(directory):
        os.makedirs(directory)


def make_config_directories():
    create_directory(config.inventory_local_directory)
    create_directory(config.switch_configs_local_directory)
    create_directory(config.logs_file_path)

def create_base_dir():
    create_directory('logs')
    create_directory('data')


import codecs
import hashlib
import logging
import os
import subprocess

from Crypto.Cipher import AES

import config
from domain.configs_management import ConfigsManagement


class ConfigsShell(ConfigsManagement):
    data_base: str = "ftp_password = \n" \
                     "grafana_password = \n" \
                     "syslog_password = \n" \
                     "ansible_password = \n" \
                     "equipments_password = \n" \
                     "ssh_password = "

    def edit_variable(self):
        try:
            with open(self.config_file_path, 'r+') as file:
                lines = file.readlines()
                variables_names = [line.split('=')[0].strip() for line in lines]

                if self.variable_name not in variables_names:
                    logging.error(
                        f'La variable {self.variable_name} n\'existe pas dans le fichier {self.config_file_path}')
                    return

                for index, line in enumerate(lines):
                    if self.variable_name in line.strip():
                        if isinstance(self.variable_value, int):
                            lines[index] = f'{self.variable_name} = {self.variable_value}\n'
                        else:
                            lines[index] = f'{self.variable_name} = "{self.variable_value}"\n'
                        break

                file.seek(0)
                file.writelines(lines)
                file.truncate()
            logging.info(f'La variable {self.variable_name} a été modifiée avec succès')

        except Exception as e:
            logging.error(f'Une erreur est survenue lors de la modification de la variable {self.variable_name} : {e}')

    @staticmethod
    def salt(salt_p):
        salt_phrase = f"$2a$12$/qzser"
        hashed_salt = hashlib.pbkdf2_hmac(hash_name='sha512', password=salt_p.encode('utf-8'),
                                          salt=salt_phrase.encode('utf-8'), iterations=100000)
        salt_hash = codecs.encode(hashed_salt, "base64")
        return salt_hash

    def modify_from_dict(self, param_dict: dict):
        self.config_file_path = f"{config.root_dir}/config.py"
        try:
            for key, value in param_dict.items():
                self.variable_name = key
                self.variable_value = value
                print(f"{key} = {value}")
                self.edit_variable()
            return True
        except Exception as err:
            return err.__str__()

    @staticmethod
    def salt_file_content(list_data: list[str] = None):
        key = ConfigsShell.salt(config.cchottsa_herbenv)[0:32]
        initial_vector = b'o\xa59\x8f\xeaf\xdc\xa477\xa1\xcfg\x87Ip'
        cipher = AES.new(key, AES.MODE_OFB, initial_vector)
        if list_data:
            ciphertext = cipher.encrypt(str.encode("\n".join(list_data)))
        else:
            with open(f"{config.clear_salt}", "rb") as file:
                plaintext = file.read()
                ciphertext = cipher.encrypt(plaintext)
            os.system(f"rm {config.clear_salt}")
        with open(f"{config.salt_file}", "wb") as file:
            file.write(ciphertext)

    @staticmethod
    def get_salt_content():
        key = ConfigsShell.salt(config.cchottsa_herbenv)[0:32]
        initial_vector = b'o\xa59\x8f\xeaf\xdc\xa477\xa1\xcfg\x87Ip'
        cipher = AES.new(key, AES.MODE_OFB, initial_vector)
        with open(f"{config.salt_file}", "rb") as file:
            ciphertext = file.read()
            plaintext = cipher.decrypt(ciphertext)
            our_salt = bytes.decode(plaintext)
        return our_salt

    @staticmethod
    def generate_salt():
        if os.path.isfile(f"{config.salt_file}"):
            our_salt = ConfigsShell.get_salt_content()
        else:
            our_salt = ConfigsShell.data_base
        with open(f"{config.clear_salt}", "w") as file:
            file.write(our_salt)

    @staticmethod
    def desalt_file_content():
        our_salt = ConfigsShell.get_salt_content()
        for salts in our_salt.split('\n'):
            if salts.startswith(config.salted_name):
                # print(salts.split(' = ')[1])
                pass
            print(salts)

    @staticmethod
    def get_value(variable: str):
        our_salt = ConfigsShell.get_salt_content()
        for salts in our_salt.split('\n'):
            if salts.split(' = ')[0] == variable:
                return salts.split(' = ')[1]
        return None

    @staticmethod
    def delete_salt(salted_name: str):
        print(f'delete {salted_name}')
        our_salt = ConfigsShell.get_salt_content()
        list_salt = our_salt.split('\n')
        new_list = []
        for salts in list_salt:
            if not salts.split(' = ')[0] == salted_name:
                new_list.append(salts)
        ConfigsShell.salt_file_content(new_list)

    @staticmethod
    def update_salt(name: str, value: str):
        print(f'update {name}, value = {value}')
        our_salt = ConfigsShell.get_salt_content()
        list_salt = our_salt.split('\n')
        new_list = []
        for salts in list_salt:
            if salts.split(' = ')[0] == name:
                new_salts = f"{name} = {value}"
                new_list.append(new_salts)
            else:
                new_list.append(salts)
        ConfigsShell.salt_file_content(new_list)

    @staticmethod
    def get_version_package(path: str = config.package_dir, env_path: str = config.env_path):
        try:
            command = f"cd {path} && source {env_path} &&  pip show aloso | grep Version"
            result = subprocess.run(command, shell=True, executable='/bin/bash', stdout=subprocess.PIPE)
            return result.stdout.decode('utf-8').split(': ')[1]
        except Exception as e:
            logging.error(f"Erreur lors de la récupération de la version : {e}")
            return ''


if __name__ == '__main__':
    # ConfigsShell.generate_salt()
    #ConfigsShell.salt_file_content()
    print(ConfigsShell.get_salt_content())
    ...

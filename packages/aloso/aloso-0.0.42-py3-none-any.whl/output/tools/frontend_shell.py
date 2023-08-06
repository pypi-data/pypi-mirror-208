import logging
import subprocess

import config
from domain.tools.frontend import Frontend


class FrontendShell(Frontend):

    @staticmethod
    def install_nodejs() -> None:
        commands: list = [
            f"wget -qO- --no-check-certificate {config.nvm_wget_url} | bash",
            "bash -c 'source ~/.bashrc && source ~/.nvm/nvm.sh && nvm install --lts'"
        ]

        try:
            print("\033[1m\033[32mInstallation de nvm et nodejs en cours...\033[0m")
            for command in commands:
                subprocess.run(command, shell=True, check=True)
            print("\033[1m\033[32mInstallation de nvm et nodejs terminée\033[0m")
            logging.info("Installation de nvm et nodejs terminée")
        except subprocess.CalledProcessError as e:
            print(f"\033[1m\033[31mErreur d'installation de nvm et nodejs : {e.output.decode('utf-8').strip()}\033[0m")
            logging.error(f"Erreur d'installation de nvm et nodejs : {e.output.decode('utf-8').strip()}")
        except Exception as e:
            print(f"\033[1m\033[31mErreur d'installation de nvm et nodejs : {e}\033[0m")
            logging.error(f"Erreur d'installation de nvm et nodejs : {e}")

    @staticmethod
    def install_nginx(app_name: str = config.application_name) -> None:

        nginx_conf_file = f"""server {{
    listen 80;
    server_name {config.frontend_host};

    root /var/www/{app_name}/dist;
    index index.html;

    location / {{
        try_files $uri /index.html;
    }}
}}
"""

        commands: list = [
            f"echo '{nginx_conf_file}' > {app_name}",
            'sudo apt update -y',
            'sudo apt install nginx -y',
            f'sudo mkdir /var/www/{app_name}',
            f"sudo mv {app_name} /etc/nginx/sites-available",
            f"sudo ln -s /etc/nginx/sites-available/{app_name} /etc/nginx/sites-enabled",
            f"sudo mv /etc/nginx/sites-enabled/default /etc/nginx/sites-enabled/default.sample",
            'sudo systemctl restart nginx'
        ]

        try:
            print("\033[1m\033[32mInstallation de nginx en cours...\033[0m")
            for command in commands:
                subprocess.run(command, shell=True, check=True)
            print("\033[1m\033[32mInstallation de nginx terminée\033[0m")
            logging.info("Installation de nginx terminée")
        except Exception as e:
            print(f"\033[1m\033[31mErreur d'installation de nginx : {e}\033[0m")
            logging.error(f"Erreur d'installation de nginx : {e}")

    @staticmethod
    def generate_app(app_name: str = config.application_name) -> None:

        commands: list = [
            f'cd {config.frontend_zip_file_dir} && unzip network-frontend-main.zip && rm network-frontend-main.zip',
            f"cd {config.frontend_zip_file_dir}/network-frontend-main && npm install && npm run build",
            f"cd /var/www/{app_name} && sudo rm -rf *",
            f"cd {config.frontend_zip_file_dir}/network-frontend-main && sudo mv dist /var/www/{app_name}",
            f"rm -r {config.frontend_zip_file_dir}/network-frontend-main",
            "sudo systemctl restart nginx"
        ]

        try:
            print("\033[1m\033[32mInstallation du projet en cours...\033[0m")
            for command in commands:
                print(f"\033[1m\033[32mExécution de la commande : {command}\033[0m")
                subprocess.run(command, shell=True, check=True)
            print("\033[1m\033[32mInstallation du projet terminée\033[0m")
            logging.info("Installation du projet terminée")
        except Exception as e:
            print(f"\033[1m\033[31mErreur d'installation du projet : {e}\033[0m")
            logging.error(f"Erreur d'installation du projet : {e}")

# Avant installation nginx :
# desinstallation Apache
# apt-get remove --purge nginx nginx-full nginx-common
# nginx -t

# Lors de la mise en place du lien symbolique, bien vérifier qu'il y ait le chemin absolu

# Edit /etc/nginx/sites-enabled/default and comment IPv6 out:
# listen [::]:80 default_server;
# https://askubuntu.com/questions/764222/nginx-installation-error-in-ubuntu-16-04

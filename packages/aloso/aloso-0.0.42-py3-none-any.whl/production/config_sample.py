import os

root_dir = os.path.dirname(os.path.abspath(__file__))
data_dir = f"{root_dir}/data"

### PARAMETRAGE

## Configuration des equipements
inventory_local_directory = f"{data_dir}/equipments/inventory"
inventory_file_name = "inventory.ini"
inventory_file_version = "new_versions.ini"
separateur = " jzycgejug  dzfejhygeu dzezed "
equipments_port = 22

## SSH connexion compte utilisateur pour execution des commandes sur une liste d'equipements
ssh_username = "user"

## Paramétrage Alias
# Type de DNS
DNS_type = "infoblox"
# DNS
alias_file = f"{data_dir}/dns/mydns.com.zone"

## Sauvegarde des fichiers de configuration des switchs datacenters
# FTP
ftp_username = 'user'
ftp_host = "1.1.1.1"
directory_ftp_switchs = '/home/dev/switchs_datacenters'
switch_configs_local_directory = f"{data_dir}/switch/switches_config"
repository_to_save_configs_for_all_switches_with_ssh = "git@gitlab.com:xxxxx/test.git"
saving_hour = "01:00"
equipement_ftp_remote_directory = "/home/developpeur/equipments_dir"

## Authentification
# Configuration LDAP pour la connexion utilisateur
ldap_host = "localhost"
ldap_port = 389
ldap_url_prefix = "developpeurconnected"
ldap_url_suffix = "com"
ldap_organization_name = "People"

# Connexion mode
connexion_mode = "local"

## ANSIBLE
# Configuration du serveur ansible où l'on se connecte pour appeler différents scripts ansible
ansible_username = ''
ansible_port = 0
ansible_host = "56.36.25.89"

### ADMINISTRATION
## Contacts Excel
excel_file_path = f"{data_dir}/site_contact.xlsx"

## LOGS
logs_file_path = f"{root_dir}/logs/operations.log"
debug_level = 10

## Base de données du portail
database_resource = "sqlite"
database_file = f"{data_dir}/database.sqlite"

## Répertoire des templates
templates_directory_path = f"{data_dir}/templates"

use_sudo = False

## INSTALLATION GRAFANA
grafana_wget_url = "https://dl.grafana.com/enterprise/release/grafana-enterprise_9.3.6_amd64.deb"
grafana_ini_file = f"{data_dir}/grafana/grafana.ini"

loki_wget_url = "https://github.com/grafana/loki/releases/download/v2.7.3/loki-linux-amd64.zip"
loki_yaml_file = f"{data_dir}/grafana/loki-local-config.yaml"
loki_service_file = f"{data_dir}/grafana/loki.service"

promtail_wget_url = "https://github.com/grafana/loki/releases/download/v2.7.3/promtail-linux-amd64.zip"
promtail_yaml_file = f"{data_dir}/grafana/promtail-local-config.yaml"
promtail_service_file = f"{data_dir}/grafana/promtail.service"

grafana_host = ""
grafana_port = 5
grafana_username = ''

# INSTALLATION FRONTEND
application_name = "network"
frontend_host = "2.1.1.4"
frontend_zip_file_dir = root_dir
nvm_wget_url = "https://raw.githubusercontent.com/nvm-sh/nvm/v0.37.2/install.sh"

# INSTALLATION NGINX
nginx_username = ''
nginx_port = 0
nginx_host = "210.256.23"
nginx_password = ""
nginx_front_build_dir = "/home/developpeur/dist"
nginx_config_file = f"{data_dir}/nginx/nginx_config"

## INSTALLATION SYSLOG
syslog_username = ''
syslog_port = 0
syslog_host = "56.25.180.2"
syslog_config_file = f"{data_dir}/syslog/syslog-ng.conf"

## Backup
backup_username = "dev"
backup_port = "40"
backup_host = "12.2.18.4"
backup_target_dir = "/home/dev/backup"
backup_hour = "23:16"
config_file = f"{root_dir}/config.py"

## Autre
cchottsa_herbenv = "/home/developpeur/test"
salted_name = "salt_1"
salt_file = f"{data_dir}/salt/.rbenv-gemsets.prod"
clear_salt = f"{data_dir}/salt/salt"

package_dir = root_dir
env_path = "venv/bin/activate"

# Equipement SSH
ssh_equipment_username = ""
ssh_equipment_port = 12
ssh_equipment_password = "hello"

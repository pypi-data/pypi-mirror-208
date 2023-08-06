# syslog_ng | base | clients | count | top_top_errors
# promtail_conf | promtail_service
# loki_conf | loki_service


syslog_ng = """
@version: 3.35

############## A LIRE
# Ce fichier se trouve dans le répertoire /etc/syslog-ng
# Il inclut les autres fichiers de configurations dans le sous dossier conf.d (présent par défaut à l'installation)
#############
# Sources
source s_file {
       network(
        transport("tcp")
        port(2222)
    );
};

template-function base-function "${MSGHDR}${MSG}";

@include "/etc/syslog-ng/conf.d/*.conf"
"""

base = """
destination logs_out {
       syslog(217.182.169.116 transport("tcp") port(1514) template("$(base-function)\n") flush-lines(1000));
};

log {
  source(s_file);
  destination(logs_out);
};
"""

clients = """
source client_src {
  file("/tmp/clients.log");
};

destination clients {
  python(
        class("TopClients")
        # Nous pouvons choisir ici-dessous le nombre de ligne qui seront envoyés maximum en une fois pour le job associé
        batch-lines(1000)
    );
};

destination client_out {
       syslog(217.182.169.116 transport("tcp") port(1519) template("${ISODATE} $(base-function)\n"));
};



log {
  source(s_file);
  destination(clients);
};

log {
  source(client_src);
  destination(client_out);
};

python {
class TopClients(object):
    
    def init(self, options):
        self.domains_dict = {}
        return True

    def send(self, msg):
        self.message = str(msg['MESSAGE'], "utf-8")
        self.date = str(msg['ISODATE'], "utf-8")
        if 'SERVFAIL' == self.message.split(" ")[-1] or 'REFUSED' == self.message.split(" ")[-1]:
          self.domains_dict[self.message.split(" ")[2].split("#")[0]] = self.domains_dict.get(self.message.split(" ")[2].split("#")[0], 0) + 1
        return self.QUEUED

    def flush(self):
        for keys, values in self.domains_dict.items():
            self.outfile = open("/tmp/clients.log", "a")
            self.outfile.write("%s Clients: %s Nombre d'erreurs: %d \n" % (self.date, keys, values))
            self.outfile.flush()
            self.outfile.close()
        self.domains_dict = {}
        return self.SUCCESS

 };
"""

count = """
source dns_src {
  file("/tmp/dns_nb_lines.log");
};

destination history_logs_lines {
  python(
        class("NbRequest")
        # Nous pouvons choisir ici-dessous le nombre de ligne qui seront envoyés maximum en une fois pour le job associé
        batch-lines(1000)
    );
};


destination dns_out {
       syslog(217.182.169.116 transport("tcp") port(1520) template("${ISODATE} $(base-function)\n"));
};


log {
  source(s_file);
  destination(history_logs_lines);
};

log {
  source(dns_src);
  destination(dns_out);
};

python {
class NbRequest(object):
    def init(self, options):
        self.counter = 0
        return True

    def send(self, msg):
        self.counter +=1
        self.date = str(msg['ISODATE'], "utf-8")
        self.host = str(msg['HOST'], "utf-8")
        return self.QUEUED

    def flush(self):

        self.outfile = open("/tmp/dns_nb_lines.log", "a")
        if self.counter != 0:
          self.outfile.write("%s %s Lines %d \n" % (self.date, self.host,self.counter))
          self.outfile.flush()
          self.outfile.close()
          self.counter = 0
        return self.SUCCESS

};
"""

top_top_errors = """
source e_src {
  file("/tmp/errors.log");
};

source d_src {
  file("/tmp/domains.log");
};

source de_src {
  file("/tmp/domains_errors.log");
};

destination e_syslog {
  python(
        class("Errors")
    );
};

destination d_syslog {
  python(
        class("TopDomains")
        # Nous pouvons choisir ici-dessous le nombre de ligne qui seront envoyés maximum en une fois pour le job associé
        batch-lines(1000)
    );
};

destination de_syslog {
  python(
        class("TopDomainsWithErrors")
        # Nous pouvons choisir ici-dessous le nombre de ligne qui seront envoyés maximum en une fois pour le job associé
        batch-lines(1000)
    );
};



destination e_out {
       syslog(217.182.169.116 transport("tcp") port(1521) template("$(base-function)\n") flush-lines(1000));
};

destination d_out {
       syslog(217.182.169.116 transport("tcp") port(1522) template("${ISODATE} $(base-function)\n"));
};
destination de_out {
       syslog(217.182.169.116 transport("tcp") port(1523) template("${ISODATE} $(base-function)\n"));
};

log {
  source(s_file);
  destination(e_syslog);
  destination(d_syslog);
  destination(de_syslog);
};


log {
  source(e_src);
  destination(e_out);
};


log {
  source(d_src);
  destination(d_out);
};

log {
  source(de_src);
  destination(de_out);
};


python {
class Errors(object):

    def send(self, msg):
        self.message = str(msg['MESSAGE'], "utf-8")
        self.date_msg = str(msg['MSGHDR'], "utf-8")

        if 'SERVFAIL' == self.message.split(" ")[-1] or 'REFUSED' == self.message.split(" ")[-1]:
            self.log_file = open("/tmp/errors.log", "a")
            self.log_file.write("%s%s \n" % (self.date_msg, self.message))
            self.log_file.flush()
            self.log_file.close()
        return True

class TopDomains(object):
    
    def init(self, options):
        self.domains_dict = {}
        return True

    def send(self, msg):
        self.message = str(msg['MESSAGE'], "utf-8")
        self.date = str(msg['ISODATE'], "utf-8")
        self.domains_dict[self.message.split(" ")[4]] = self.domains_dict.get(self.message.split(" ")[4], 0) + 1
        return self.QUEUED

    def flush(self):
        for keys, values in self.domains_dict.items():
            self.outfile = open("/tmp/domains.log", "a")
            self.outfile.write("%s Domaine: %s Nombre de requetes: %d \n" % (self.date, keys, values))
            self.outfile.flush()
            self.outfile.close()
        self.domains_dict = {}
        return self.SUCCESS

class TopDomainsWithErrors(object):

    def init(self, options):
        self.domains_dict = {}
        return True

    def send(self, msg):
        self.message = str(msg['MESSAGE'], "utf-8")
        self.date = str(msg['ISODATE'], "utf-8")
        if 'SERVFAIL' == self.message.split(" ")[-1] or 'REFUSED' == self.message.split(" ")[-1]:
            self.domains_dict[self.message.split(" ")[4]] = self.domains_dict.get(self.message.split(" ")[4], 0) + 1
        return self.QUEUED

    def flush(self):
        for keys, values in self.domains_dict.items():
            self.outfile = open("/tmp/domains_errors.log", "a")
            self.outfile.write("%s Domaine: %s Nombre d'erreurs: %d \n" % (self.date, keys, values))
            self.outfile.flush()
            self.outfile.close()
        self.domains_dict = {}
        return self.SUCCESS

};
"""

promtail_conf = """
server:
  http_listen_port: 9080
  grpc_listen_port: 0

positions:
  filename: /data/loki/positions.yaml

clients:
  - url: http://localhost:3100/loki/api/v1/push

scrape_configs:
  - job_name: clients
    syslog:
      listen_address: 0.0.0.0:1519
      idle_timeout: 60s
      label_structured_data: yes
      labels:
        job: "clients"
    relabel_configs:
      - source_labels: [ '__syslog_message_hostname' ]
        target_label: 'host'

  - job_name: dns
    syslog:
      listen_address: 0.0.0.0:1520
      idle_timeout: 60s
      label_structured_data: yes
      labels:
        job: "dns"
    relabel_configs:
      - source_labels: [ '__syslog_message_hostname' ]
        target_label: 'host'

  - job_name: errors
    syslog:
      listen_address: 0.0.0.0:1521
      idle_timeout: 60s
      label_structured_data: yes
      labels:
        job: "errors"
    relabel_configs:
      - source_labels: [ '__syslog_message_hostname' ]
        target_label: 'host'

  - job_name: domains
    syslog:
      listen_address: 0.0.0.0:1522
      idle_timeout: 60s
      label_structured_data: yes
      labels:
        job: "domains"
    relabel_configs:
      - source_labels: [ '__syslog_message_hostname' ]
        target_label: 'host'

  - job_name: domains_errors
    syslog:
      listen_address: 0.0.0.0:1523
      idle_timeout: 60s
      label_structured_data: yes
      labels:
        job: "domains_errors"
    relabel_configs:
      - source_labels: [ '__syslog_message_hostname' ]
        target_label: 'host'

  - job_name: syslog
    syslog:
      listen_address: 0.0.0.0:1514
      idle_timeout: 60s
      label_structured_data: yes
      labels:
        job: "syslog"
    relabel_configs:
      - source_labels: [ '__syslog_message_hostname' ]
        target_label: 'host'


"""

promtail_service = """
[Unit]
Description=Promtail service
After=network.target

[Service]
Type=simple
User=root
ExecStart=/usr/local/bin/promtail -config.file /etc/promtail-local-config.yaml

[Install]
WantedBy=multi-user.target
"""

loki_conf = """
auth_enabled: false

server:
  http_listen_port: 3100

distributor:
  ring:
    kvstore:
      store: memberlist

ingester:
  lifecycler:
    ring:
      kvstore:
        store: inmemory
      replication_factor: 1
    final_sleep: 0s
  chunk_idle_period: 5m
  chunk_retain_period: 30s

schema_config:
  configs:
    - from: 2023-03-10
      store: boltdb-shipper
      object_store: filesystem
      schema: v11
      index:
        prefix: index_
        period: 24h

storage_config:
  boltdb_shipper:
    active_index_directory: /data/loki/index
    cache_location: /data/loki/index_cache
    cache_ttl: 24h
    shared_store: filesystem

  filesystem:
    directory: /data/loki/chunks

compactor:
  working_directory: /data/loki/compactor
  shared_store: filesystem
  compaction_interval: 10m
  retention_enabled: true
  retention_delete_delay: 10s
  retention_delete_worker_count: 150

limits_config:
  retention_period: 48h
  enforce_metric_name: false
  reject_old_samples: true
  reject_old_samples_max_age: 168h
  retention_stream:
    - selector: '{job="syslog"}'
      priority: 2
      period: 24h

chunk_store_config:
  max_look_back_period: 0s

query_scheduler:
  max_outstanding_requests_per_tenant: 2048
"""

loki_service = """
[Unit]
Description=Loki service
After=network.target

[Service]
Type=simple
User=root
ExecStart=/usr/local/bin/loki -config.file /etc/loki-local-config.yaml

[Install]
WantedBy=multi-user.target
"""

config_sample = """
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

"""

backend_service = """
[Unit]
Description=Gunicorn Daemon for FastAPI Application
After=network.target

[Service]
User=bacari
Group=sudo
WorkingDirectory=/home/developpeur/Project/network-backend-switch_merge
ExecStart=/home/developpeur/Project/network-backend-switch_merge/env/bin/gunicorn api.server:app -k uvicorn.workers.UvicornWorker --bind 217.182.169.116:8002 --access-logfile /home/developpeur/Project/network-backend-switch_merge/logs/access_log.log --error-logfile /home/developpeur/Project/network-backend-switch_merge/logs/error_log.log --log-level debug

[Install]
WantedBy=multi-user.target
"""

backup_service = """
[Unit]
Description=Sauvegarde automatique du dossier data
After=network.target

[Service]
User=developpeur
Group=sudo
WorkingDirectory=/home/developpeur/auto-backup
ExecStart=/bin/bash -c 'source /home/developpeur/auto-backup/env/bin/activate && python3 /home/developpeur/auto-backup/script.py'
Restart=on-failure

[Install]
WantedBy=multi-user.target
"""

nginx_service = """
# Stop dance for nginx
# =======================
#
# ExecStop sends SIGSTOP (graceful stop) to the nginx process.
# If, after 5s (--retry QUIT/5) nginx is still running, systemd takes control
# and sends SIGTERM (fast shutdown) to the main process.
# After another 5s (TimeoutStopSec=5), and if nginx is alive, systemd sends
# SIGKILL to all the remaining processes in the process group (KillMode=mixed).
#
# nginx signals reference doc:
# http://nginx.org/en/docs/control.html
#
[Unit]
Description=A high performance web server and a reverse proxy server
Documentation=man:nginx(8)
Wants=backend.service backup.service watch-config.service
After=network.target nss-lookup.target backend.service backup.service watch-config.service

[Service]
Type=forking
PIDFile=/run/nginx.pid
ExecStartPre=/usr/sbin/nginx -t -q -g 'daemon on; master_process on;'
ExecStart=/usr/sbin/nginx -g 'daemon on; master_process on;'
ExecReload=/usr/sbin/nginx -g 'daemon on; master_process on;' -s reload
ExecStop=-/sbin/start-stop-daemon --quiet --stop --retry QUIT/5 --pidfile /run/nginx.pid
TimeoutStopSec=5
KillMode=mixed

[Install]
WantedBy=multi-user.target

"""

watch_config_service = """
[Unit]
Description=Watchdog Daemon to Reload Gunicorn
After=network.target


[Service]
User=dev
Group=sudo
WorkingDirectory=/home/bacari/Documents/Projects/pythonProject
ExecStart= watchmedo shell-command --patterns="config.py" --command="kill -HUP $(systemctl status backend |  sed -n 's/.*Main PID: \(.*\)$/\1/g p' | cut -f1 -d' ')" /home/bacari/Documents/Projects/pythonProject


[Install]
WantedBy=multi-user.target
"""

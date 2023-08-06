import logging

from fabric import Connection, Config
from patchwork.files import exists

import config
from domain.tools.grafana import Grafana


class GrafanaShell(Grafana):
    @staticmethod
    def connection():
        configuration = Config(overrides={'user': config.grafana_username,
                                          'port': config.grafana_port,
                                          'sudo': {'password': config.grafana_password}})
        try:
            conn = Connection(host=config.grafana_host, config=configuration)
            return conn
        except Exception as e:
            logging.error(f"Erreur de connexion au serveur : {e}")

    @staticmethod
    def install_grafana():
        conn = GrafanaShell.connection()

        grafana_deb_file = config.grafana_wget_url.split("/")[-1]

        if exists(conn, grafana_deb_file):
            commands = [
                'apt-get install -y adduser libfontconfig1',
                f'dpkg -i {grafana_deb_file}',
                f'rm {grafana_deb_file}',
                'mv grafana.ini /etc/grafana/grafana.ini',
                'systemctl daemon-reload',
                'systemctl restart grafana-server'
            ]
        else:
            commands = [
                'apt-get install -y adduser libfontconfig1',
                f'wget --no-check-certificate {config.grafana_wget_url}',
                f'dpkg -i {grafana_deb_file}',
                f'rm {grafana_deb_file}',
                'mv grafana.ini /etc/grafana/grafana.ini',
                'systemctl daemon-reload',
                'systemctl restart grafana-server'
            ]

        conn.put(config.grafana_ini_file)
        logging.info("Fichier de configuration de Grafana envoyé")

        try:
            for command in commands:
                if config.use_sudo:
                    conn.sudo(command)
                else:
                    conn.run(command)
            logging.info("Grafana installé avec succès")
        except Exception as e:
            logging.error(f"Erreur d'installaton de Grafana : {e}")

    @staticmethod
    def install_loki():
        conn = GrafanaShell.connection()

        loki_zip_file = config.loki_wget_url.split("/")[-1]

        conn.put(config.loki_yaml_file)
        conn.put(config.loki_service_file)

        if exists(conn, loki_zip_file):
            commands = [
                f"unzip {loki_zip_file}",
                f"rm {loki_zip_file}",
                "mv loki-linux-amd64 /usr/local/bin/loki",
                "mkdir -p /data/loki",
                "mv loki-local-config.yaml /etc/loki-local-config.yaml",
                "mv loki.service /etc/systemd/system/loki.service",
                "systemctl daemon-reload",
                "systemctl start loki.service"
            ]
        else:
            commands = [
                f"wget --no-check-certificate {config.loki_wget_url}",
                f"unzip {loki_zip_file}",
                f"rm {loki_zip_file}",
                "mv loki-linux-amd64 /usr/local/bin/loki",
                "mkdir -p /data/loki",
                "mv loki-local-config.yaml /etc/loki-local-config.yaml",
                "mv loki.service /etc/systemd/system/loki.service",
                "systemctl daemon-reload",
                "systemctl start loki.service"
            ]

        try:
            for command in commands:
                if config.use_sudo:
                    conn.sudo(command)
                else:
                    conn.run(command)
            logging.info("Loki installé avec succès")
        except Exception as e:
            logging.error(f"Erreur d'installaton de Loki : {e}")

    @staticmethod
    def install_promtail():
        conn = GrafanaShell.connection()

        promtail_zip_file = config.promtail_wget_url.split("/")[-1]

        conn.put(config.promtail_yaml_file)
        conn.put(config.promtail_service_file)

        if exists(conn, promtail_zip_file):
            commands = [
                f"unzip {promtail_zip_file}",
                f"rm {promtail_zip_file}",
                "mv promtail-linux-amd64 /usr/local/bin/promtail",
                "mv promtail-local-config.yaml /etc/promtail-local-config.yaml",
                "mv promtail.service /etc/systemd/system/promtail.service",
                "systemctl daemon-reload",
                "systemctl start promtail.service"
            ]
        else:
            commands = [
                f"wget --no-check-certificate {config.promtail_wget_url}",
                f"unzip {promtail_zip_file}",
                f"rm {promtail_zip_file}",
                "mv promtail-linux-amd64 /usr/local/bin/promtail",
                "mv promtail-local-config.yaml /etc/promtail-local-config.yaml",
                "mv promtail.service /etc/systemd/system/promtail.service",
                "systemctl daemon-reload",
                "systemctl start promtail.service"
            ]

        try:
            for command in commands:
                if config.use_sudo:
                    conn.sudo(command)
                else:
                    conn.run(command)
            logging.info("Promtail installé avec succès")
        except Exception as e:
            logging.error(f"Erreur d'installaton de Promtail : {e}")

    @staticmethod
    def remove_grafana():
        conn = GrafanaShell.connection()
        commands = [
            'systemctl stop grafana-server',
            'dpkg -P grafana-enterprise',
            'rm -r /etc/grafana',
            'systemctl daemon-reload',
        ]
        for command in commands:
            if config.use_sudo:
                conn.sudo(command)
            else:
                conn.run(command)

    @staticmethod
    def install_all():
        GrafanaShell.install_grafana()
        GrafanaShell.install_loki()
        GrafanaShell.install_promtail()

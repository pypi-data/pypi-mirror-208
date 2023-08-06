import logging

from fabric import Connection, Config
import config
from domain.tools.nginx import Nginx


class SyslogShell(Nginx):

    @staticmethod
    def connection():
        configuration = Config(overrides={'user': config.syslog_username,
                                          'port': config.syslog_port,
                                          'sudo': {'password': config.syslog_password}})
        try:
            conn = Connection(host=config.syslog_host, config=configuration)
            return conn
        except Exception as e:
            logging.error(f"Erreur de connexion au serveur : {e}")

    @staticmethod
    def install_syslog():
        conn = SyslogShell.connection()

        conn.put(config.syslog_config_file)

        if config.use_sudo:
            conn.sudo('apt update')
            conn.sudo('apt install syslog-ng -y')
            conn.sudo('mv /etc/syslog-ng/syslog-ng.conf /etc/syslog-ng/syslog-ng.sample')
            conn.sudo('mv syslog-ng.conf /etc/syslog-ng/syslog-ng.conf')
        else:
            conn.run('apt update')
            conn.run('apt install syslog-ng -y')
            conn.run('mv /etc/syslog-ng/syslog-ng.conf /etc/syslog-ng/syslog-ng.sample')
            conn.run('mv syslog-ng.conf /etc/syslog-ng/syslog-ng.conf')

        logging.info("Installation de syslog-ng terminée")

import config
from domain.record_dns import Alias


class Bind9(Alias):

    def get_records(self, alias_file_path: str = config.alias_file):
        with open(alias_file_path, "r") as file:
            lines = file.readlines()
            for line in lines:
                line = line.strip()
                if " A " in line:
                    self.open_data.append(line.split(" ")[0])

    def create_alias(self, server_ip: str, alias_file_path: str = config.alias_file):
        if not self.alias_is_available():
            return
        with open(alias_file_path, "a") as file:
            file.write(f"{self.name} IN A {server_ip}\n")
        self.open_data.append(self.name)

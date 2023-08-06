import json

import requests
from dataclasses import dataclass

from domain.record_dns import Alias


@dataclass
class InfoBlox(Alias):

    def get_records(self, alias_file_path: str):
        "https://1.1.1.1/wapi/v2.12"
        infoblox_url = 'https://1.1.1.1/wapi/v2.12'
        auth = ('username', 'password')

        endpoint = '/record:host'
        params = {
            '_return_fields+': 'extattrs',
            '_max_results': 0
        }

        response = requests.get(infoblox_url + endpoint, params=params, auth=auth, verify=False)

        if response.status_code == 200:
            records = response.json()
            print(records)
        else:
            print(f'Error {response.status_code}: {response.text}')

    def create_alias(self, server_ip: str, alias_file_path: str):
        pass

    def create_infoblox_record(self, ip_address, hostname, domain, api_endpoint, api_key):
        url = f"{api_endpoint}/record:host"
        headers = {'Content-type': 'application/json', 'Authorization': f'Token {api_key}'}

        data = {
            "ipv4addrs": [
                {
                    "ipv4addr": ip_address
                }
            ],
            "name": hostname,
            "view": "default",
            "zone": domain
        }

        response = requests.post(url, headers=headers, data=json.dumps(data), verify=False)

        if response.status_code == requests.codes.created:
            print(f"Alias créé {hostname}.{domain}")
        else:
            print(f"Erreur lors de la création de l'alias: {response.content}")


if __name__ == "__main__":
    # requests.packages.urllib3.disable_warnings()
    # url = "https://1.1.1.1/wapi/v2.10/record:host?_return_as_object=1"
    # data = requests.request("GET", url, auth=('admin', 'Infoblox'), verify=False)
    # print(data.text)

    infoblox = InfoBlox()
    infoblox.get_records(alias_file_path="")

# import requests

from domain.cisco_prime import CiscoPrime


class CiscoPrimeOutput(CiscoPrime):

    @staticmethod
    def get_all_devices():
        """  https://1.1.1.1/webacs/api/v4/data/Devices"""

        cisco_prime_url = 'https://1.1.1.1/webacs/api/v4/data/Devices'
        auth = ('username', 'password')
        '''
        response = requests.get(cisco_prime_url, auth=auth, verify=False)

        if response.status_code == 200:
            records = response.json()
            # print(records)
        else:
            # print(f'Error {response.status_code}: {response.text}')
            ...
        '''

        sample_response_v1 = {
            "mgmtResponse": {
                "@requestUrl": "https://localhost/webacs/api/v4/op/devices/exportDevices",
                "@responseType": "operation",
                "@rootUrl": "https://localhost/webacs/api/v4/op",
                "devicesExportResult": [{
                    "devices": {
                        "device": [{
                            "cliEnablePassword": "String value",
                            "cliPassword": "String value",
                            "cliRetries": "String value",
                            "cliTimeout": "String value",
                            "cliUsername": "String value",
                            "credentialProfileName": "String value",
                            "httpConfigPassword": "String value",
                            "httpConfigUsername": "String value",
                            "httpMonitorPassword": "String value",
                            "httpMonitorUsername": "String value",
                            "httpPort": "223",
                            "httpServer": "cisco1",
                            "ipAddress": "231.155.18.8",
                            "networkMask": "String value",
                            "protocol": "String value",
                            "snmpCommunity": "String value",
                            "snmpPort": "String value",
                            "snmpReadCommunity": "String value",
                            "snmpRetries": "String value",
                            "snmpTimeout": "String value",
                            "snmpVersion": "String value",
                            "snmpWriteCommunity": "String value",
                            "snmpv3AuthPassword": "String value",
                            "snmpv3AuthType": "String value",
                            "snmpv3PrivacyPassword": "String value",
                            "snmpv3PrivacyType": "String value",
                            "snmpv3UserName": "String value",
                            "udfs": {
                                "udf": [{
                                    "name": "String value",
                                    "value": "String value"
                                }, {
                                    "name": "Another string value",
                                    "value": "Another string value"
                                }]
                            }
                        }, {
                            "cliEnablePassword": "Another string value",
                            "cliPassword": "Another string value",
                            "cliRetries": "Another string value",
                            "cliTimeout": "Another string value",
                            "cliUsername": "Another string value",
                            "credentialProfileName": "Another string value",
                            "httpConfigPassword": "Another string value",
                            "httpConfigUsername": "Another string value",
                            "httpMonitorPassword": "Another string value",
                            "httpMonitorUsername": "Another string value",
                            "httpPort": "789",
                            "httpServer": "cisco2",
                            "ipAddress": "211.255.199.9",
                            "networkMask": "Another string value",
                            "protocol": "Another string value",
                            "snmpCommunity": "Another string value",
                            "snmpPort": "Another string value",
                            "snmpReadCommunity": "Another string value",
                            "snmpRetries": "Another string value",
                            "snmpTimeout": "Another string value",
                            "snmpVersion": "Another string value",
                            "snmpWriteCommunity": "Another string value",
                            "snmpv3AuthPassword": "Another string value",
                            "snmpv3AuthType": "Another string value",
                            "snmpv3PrivacyPassword": "Another string value",
                            "snmpv3PrivacyType": "Another string value",
                            "snmpv3UserName": "Another string value",
                            "udfs": {
                                "udf": [{
                                    "name": "String value",
                                    "value": "String value"
                                }, {
                                    "name": "Another string value",
                                    "value": "Another string value"
                                }]
                            }
                        }]
                    }
                }]
            }
        }

        sample_response_v2 = {
            "queryResponse": {
                "@type": "Devices",
                "@requestUrl": "https://localhost/webacs/api/v4/data/Devices/15",
                "@responseType": "getEntity",
                "@rootUrl": "https://localhost/webacs/api/v4/data",
                "entity": [{
                    "@dtoType": "devicesDTO",
                    "@type": "Devices",
                    "@url": "https://localhost/webacs/api/v4/data/Devices/15",
                    "devicesDTO": {
                        "@displayName": "String value",
                        "@id": 15,
                        "@uuid": "String value",
                        "adminStatus": "UNMANAGED",
                        "collectionDetail": "String value",
                        "collectionStatus": "COMPLETED",
                        "collectionTime": "1986-07-23T16:00:00.000Z",
                        "creationTime": "1986-07-23T16:00:00.000Z",
                        "deviceId": 15,
                        "deviceName": "cisco1",
                        "deviceType": "String value",
                        "ipAddress": "231.155.18.8",
                        "location": "String value",
                        "managementStatus": "UNKNOWN",
                        "manufacturerPartNrs": {
                            "manufacturerPartNr": [{
                                "name": "String value",
                                "partNumber": "String value",
                                "serialNumber": "String value"
                            }, {
                                "name": "Another string value",
                                "partNumber": "Another string value",
                                "serialNumber": "Another string value"
                            }]
                        },
                        "productFamily": "String value",
                        "reachability": "UNKNOWN",
                        "softwareType": "String value",
                        "softwareVersion": "String value"
                    }
                }, {
                    "@dtoType": "devicesDTO",
                    "@type": "Devices",
                    "@url": "https://localhost/webacs/api/v4/data/Devices/15",
                    "devicesDTO": {
                        "@displayName": "String value",
                        "@id": 15,
                        "@uuid": "String value",
                        "adminStatus": "UNMANAGED",
                        "collectionDetail": "String value",
                        "collectionStatus": "COMPLETED",
                        "collectionTime": "1986-07-23T16:00:00.000Z",
                        "creationTime": "1986-07-23T16:00:00.000Z",
                        "deviceId": 15,
                        "deviceName": "cisco2",
                        "deviceType": "String value",
                        "ipAddress": "211.255.199.9",
                        "location": "String value",
                        "managementStatus": "UNKNOWN",
                        "manufacturerPartNrs": {
                            "manufacturerPartNr": [{
                                "name": "String value",
                                "partNumber": "String value",
                                "serialNumber": "String value"
                            }, {
                                "name": "Another string value",
                                "partNumber": "Another string value",
                                "serialNumber": "Another string value"
                            }]
                        },
                        "productFamily": "String value",
                        "reachability": "UNKNOWN",
                        "softwareType": "String value",
                        "softwareVersion": "String value"
                    }
                }, {
                    "@dtoType": "devicesDTO",
                    "@type": "Devices",
                    "@url": "https://localhost/webacs/api/v4/data/Devices/15",
                    "devicesDTO": {
                        "@displayName": "String value",
                        "@id": 15,
                        "@uuid": "String value",
                        "adminStatus": "UNMANAGED",
                        "collectionDetail": "String value",
                        "collectionStatus": "COMPLETED",
                        "collectionTime": "1986-07-23T16:00:00.000Z",
                        "creationTime": "1986-07-23T16:00:00.000Z",
                        "deviceId": 15,
                        "deviceName": "cisco3",
                        "deviceType": "String value",
                        "ipAddress": "242.131.2.2",
                        "location": "String value",
                        "managementStatus": "UNKNOWN",
                        "manufacturerPartNrs": {
                            "manufacturerPartNr": [{
                                "name": "String value",
                                "partNumber": "String value",
                                "serialNumber": "String value"
                            }, {
                                "name": "Another string value",
                                "partNumber": "Another string value",
                                "serialNumber": "Another string value"
                            }]
                        },
                        "productFamily": "String value",
                        "reachability": "UNKNOWN",
                        "softwareType": "String value",
                        "softwareVersion": "String value"
                    }
                }]
            }
        }

        return sample_response_v2

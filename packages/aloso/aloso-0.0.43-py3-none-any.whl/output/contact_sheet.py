from dataclasses import dataclass

import pandas as pd
import sqlite3
import config
from domain.contact import Contact


@dataclass
class ContactSheet(Contact):

    def __str__(self):
        # Test done
        return f"Nom: {self.name}\nPrénom: {self.firstname}\nMail: {self.mail}\nTéléphone: {self.tel}"

    @staticmethod
    def get_contact_line_site_by_name(site_name: str, file_path: str = config.excel_file_path):
        # Test done
        data_frame = pd.read_excel(file_path, dtype='object')
        return data_frame.loc[data_frame['Nom du site'] == site_name]

    def load_contact(self, site_name: str, file_path: str = config.excel_file_path):
        # Test done
        try:
            data_frame = self.get_contact_line_site_by_name(site_name, file_path)
            self.name = data_frame['Nom'].values[0]
            self.firstname = data_frame['Prénom'].values[0]
            self.mail = data_frame['Mail'].values[0]
            self.tel = data_frame['Téléphone'].values[0]
        except IndexError:
            print(f"Le site {site_name} n'existe pas dans le fichier de contact")

    @staticmethod
    def get_all_contact_json(file_path: str = config.excel_file_path):
        data_frame = pd.read_excel(file_path, dtype='object')
        json_contact_list = {}
        for index, row in data_frame.iterrows():
            json_contact_list[row['Nom du site']] = {
                "Nom": row['Nom'],
                "Prénom": row['Prénom'],
                "Mail": row['Mail'],
                "Téléphone": row['Téléphone']
            }
        return json_contact_list

if __name__ == '__main__':
    contact_sheet = ContactSheet()
    # print(contact_sheet.get_contact_line_site_by_name(""))
    contact_sheet.load_contact("Site-1")
    print(contact_sheet.tel)
    print(contact_sheet)
    print(contact_sheet.get_all_contact_json())

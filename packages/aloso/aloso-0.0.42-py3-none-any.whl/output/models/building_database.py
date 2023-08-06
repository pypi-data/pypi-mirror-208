import logging
from typing import Optional

from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import sessionmaker, relationship, joinedload

import config
from domain.building import Building
from domain.equipment_management import Equipments
from output.database.database_base import Base, engine
from output.shell.shell import Shell


class BuildingData(Base, Building):
    __tablename__ = "Building"

    id = Column(Integer, primary_key=True)
    name = Column(String(50))
    equipments = relationship("EquipmentsData", back_populates="building")

    # OK
    def create(self):
        try:
            with sessionmaker(bind=engine)() as session:
                session.add(self)
                session.commit()
                logging.info("Bâtiment ajouté dans la base de données")
        except Exception as e:
            logging.error(e)

    # OK
    def delete(self):
        try:
            with sessionmaker(bind=engine)() as session:
                wifi_data = session.query(BuildingData).filter(BuildingData.id == self.id).one()
                session.delete(wifi_data)
                session.commit()
                logging.info("Bâtiment supprimé de la base de données")
        except Exception as e:
            logging.error(e)

    # OK
    def update(self):
        try:
            assert self.id is not None
            with sessionmaker(bind=engine)() as session:
                wifi_data = session.query(BuildingData).filter(BuildingData.id == self.id).one()
                wifi_data.name = self.name
                session.commit()
                logging.info("Bâtiment mis à jour dans la base de données")
        except Exception as e:
            logging.error(f"Erreur lors de la mise à jour du bâtiment : {e}")

    # OK
    @staticmethod
    def get_by_name(name: str):
        try:
            with sessionmaker(bind=engine)() as session:
                return (
                    session.query(BuildingData)
                    .options(joinedload(BuildingData.equipments))
                    .filter(BuildingData.name == name)
                    .first()
                )
        except Exception as e:
            logging.error(e)
            return None

    # OK
    @staticmethod
    def get_by_id(b_id: int):
        try:
            with sessionmaker(bind=engine)() as session:
                return (
                    session.query(BuildingData)
                    .options(joinedload(BuildingData.equipments))
                    .filter(BuildingData.id == b_id)
                    .first()
                )
        except Exception as e:
            logging.error(e)
            return None

    # OK
    @staticmethod
    def get_all() -> Optional[dict]:

        try:
            with sessionmaker(bind=engine)() as session:
                data = session.query(BuildingData).all()
                json_all_buildings = {}

                for building in data:
                    json_all_buildings[building.id] = {
                        "id": building.id,
                        "name": building.name,
                        "equipments": building.equipments
                    }
                return json_all_buildings
        except Exception as e:
            logging.error(e)
            return None

    # OK
    def link_equipment(self, equipment: Equipments):
        try:
            assert self.id is not None
            with sessionmaker(bind=engine)() as session:
                self.equipments.append(equipment)
                # equipment.wifi = self
                session.add(self)
                session.commit()
                logging.info(f"Equipement {equipment} associé au bâtiment {self}")
        except Exception as e:
            logging.error(f"Erreur lors de l'association de l'équipement {equipment} au bâtiment {self} : {e}")

    # OK
    def unlink_equipment(self, equipment: Equipments):
        try:
            assert self.id is not None
            with sessionmaker(bind=engine)() as session:
                self.equipments.remove(equipment)
                # equipment.wifi = None
                session.add(self)
                session.commit()
                logging.info(f"Equipement {equipment} dissocié du bâtiment {self}")
        except Exception as e:
            logging.error(f"Erreur lors de la dissociation de l'équipement {equipment} du bâtiment {self} : {e}")

    def execute(self, *args):
        conn = Shell.ssh_connection(host=self.equipment.ip,
                                    username=config.ssh_equipment_username,
                                    password=config.ssh_equipment_password,
                                    port=config.ssh_equipment_port)

        cmd = "energywise query importance 75 name set level 10" if args[0] is None else args[0]

        try:
            with conn:
                conn.run(cmd)
            print(f"Commande {cmd} executé avec succès")
        except Exception as e:
            print(f"Erreur d'execution de la commande : {e}")

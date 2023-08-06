import logging

from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import sessionmaker, relationship

from domain.equipments_group import EquipmentsGroup
from output.database.database_base import Base, engine
from output.models.equipments_database import EquipmentsData


class EquipmentsGroupData(Base, EquipmentsGroup):
    __tablename__ = "EquipmentsGroup"

    id = Column(Integer, primary_key=True)
    name = Column(String(50))
    equipment = relationship("EquipmentsData", back_populates="group", cascade="all, delete-orphan")

    @staticmethod
    def get_all():
        try:
            with sessionmaker(bind=engine)() as session:
                data_groups = session.query(EquipmentsGroupData).all()
                data_equipments = session.query(EquipmentsData).all()
                json_all_equipments = []
                json_all_groups = {}

                for group in data_groups:
                    for equipment in data_equipments:
                        if equipment.id_group == group.id:
                            my_equipment = {
                                "name": equipment.name,
                                "ip": equipment.ip,
                                "version": equipment.version,
                                "id_equipment": equipment.id,
                                "id_group": equipment.id_group,
                            }
                            json_all_equipments.append(my_equipment)
                    json_all_groups[group.name] = json_all_equipments
                    json_all_equipments = []

                return json_all_groups
        except Exception as e:
            logging.error(e)

    @staticmethod
    def get_group_equipment_by_id(id_group):
        try:
            with sessionmaker(bind=engine)() as session:
                return session.query(EquipmentsGroupData).filter(EquipmentsGroupData.id == id_group).first()
        except Exception as e:
            logging.error(e)

    def create(self):
        try:
            with sessionmaker(bind=engine)() as session:
                session.add(self)
                session.commit()
                logging.info("Equipment Group database : create : ok")
        except Exception as e:
            logging.error(e)

    def update(self):
        try:
            with sessionmaker(bind=engine)() as session:
                session.merge(self)
                session.commit()
                logging.info("Equipment Group database : update : ok")
        except Exception as e:
            logging.error(e)

    def delete(self):
        try:
            with sessionmaker(bind=engine)() as session:
                session.delete(self.get_group_equipment_by_id(self.id))
                session.commit()
                logging.info("Equipment Group database : delete : ok")
                return True
        except Exception as e:
            logging.error(e)
            return False

    def new_group_and_equipments(self, new_name_group, list_equipments):
        try:
            self.name = new_name_group
            self.create()
            for equipments_data in list_equipments:
                new_equipment = EquipmentsData(name=equipments_data.split(' ')[0], ip=equipments_data.split(' ')[1])
                new_equipment.version = new_equipment.get_equipment_version(command='')
                new_equipment.group = self
                new_equipment.create()
            return True
        except Exception as e:
            logging.error(e)
            return False

    @staticmethod
    def update_group_and_equipments(my_group, name_group, list_values):
        try:
            my_group.delete()
            new_group = EquipmentsGroupData()
            return new_group.new_group_and_equipments(name_group, list_values)
        except Exception as e:
            logging.error(e)
            return False

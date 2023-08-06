from sqlalchemy import Column, Integer, String, ForeignKey
import logging

from sqlalchemy.orm import sessionmaker, relationship

from domain.equipment_management import Equipments
from output.database.database_base import Base, engine


class EquipmentsData(Base, Equipments):
    __tablename__ = "Equipments"

    id = Column(Integer, primary_key=True)
    name = Column(String(50))
    ip = Column(String(50))
    version = Column(String(50), default='V1.0')
    id_group = Column(Integer, ForeignKey('EquipmentsGroup.id', ondelete='CASCADE'))
    group = relationship("EquipmentsGroupData", back_populates="equipment")
    building_id = Column(Integer, ForeignKey('Building.id', ondelete='SET NULL'), nullable=True)
    building = relationship("BuildingData", back_populates="equipments")

    @staticmethod
    def get_all():
        try:
            with sessionmaker(bind=engine)() as session:
                return session.query(EquipmentsData).all()
        except Exception as e:
            logging.error(e)

    @staticmethod
    def get_equipment_by_id(id_equipment):
        try:
            with sessionmaker(bind=engine)() as session:
                return session.query(EquipmentsData).filter(EquipmentsData.id == id_equipment).first()
        except Exception as e:
            logging.error(e)

    @staticmethod
    def get_equipments_by_group_id(id_group):
        try:
            with sessionmaker(bind=engine)() as session:
                return session.query(EquipmentsData).filter(EquipmentsData.id_group == id_group).all()
        except Exception as e:
            logging.error(e)

    def create(self):
        try:
            with sessionmaker(bind=engine)() as session:
                session.add(self)
                session.commit()
                logging.info("Equipment database : create : ok")
                return True
        except Exception as e:
            logging.error(e)
            return False

    def update(self):
        try:
            with sessionmaker(bind=engine)() as session:
                session.merge(self)
                session.commit()
                logging.info("Equipment database : update : ok")
                return True
        except Exception as e:
            logging.error(e)
            return False

    def delete(self):
        try:
            with sessionmaker(bind=engine)() as session:
                session.delete(self.get_equipment_by_id(self.id))
                session.commit()
                logging.info("Equipment database : delete : ok")
                return True
        except Exception as e:
            logging.error(e)
            return False

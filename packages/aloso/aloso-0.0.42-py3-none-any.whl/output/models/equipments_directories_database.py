import logging

from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import sessionmaker

from domain.equipments_directories import EquipmentsDirectories
from output.database.database_base import Base, engine


class EquipmentsDirectoriesData(Base, EquipmentsDirectories):
    __tablename__ = "EquipmentsDir"

    id = Column(Integer, primary_key=True)
    name = Column(String(50))
    frequency = Column(Integer, default=1)

    @staticmethod
    def get_all():
        try:
            with sessionmaker(bind=engine)() as session:
                data = session.query(EquipmentsDirectoriesData).all()
                json_all_directories = {}
                for equipment_dir in data:
                    json_all_directories[equipment_dir.id] = {
                        "id": equipment_dir.id,
                        "name": equipment_dir.name,
                        "frequency": equipment_dir.frequency}
                return json_all_directories
        except Exception as e:
            logging.error(e)

    @staticmethod
    def get_equipment_by_id(id_equipment):
        try:
            with sessionmaker(bind=engine)() as session:
                return session.query(EquipmentsDirectoriesData).filter(EquipmentsDirectoriesData.id == id_equipment).first()
        except Exception as e:
            logging.error(e)

    def create(self):
        try:
            with sessionmaker(bind=engine)() as session:
                session.add(self)
                session.commit()
                logging.info("Equipment Directories database : create : ok")
        except Exception as e:
            logging.error(e)

    def update(self):
        try:
            with sessionmaker(bind=engine)() as session:
                session.merge(self)
                session.commit()
                logging.info("Equipment Directories database : update : ok")
        except Exception as e:
            logging.error(e)

    def delete(self):
        try:
            with sessionmaker(bind=engine)() as session:
                session.delete(self.get_equipment_by_id(self.id))
                session.commit()
                logging.info("Equipment Directories database : delete : ok")
        except Exception as e:
            logging.error(e)


if __name__ == '__main__':
    equipment1 = EquipmentsDirectoriesData(name='Switchs', frequency=2)
    equipment2 = EquipmentsDirectoriesData(name='Bornes', frequency=1)

    # equipment1.create()
    # equipment2.create()

    print(EquipmentsDirectoriesData.get_all())

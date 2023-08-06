import logging

from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import sessionmaker

from domain.favorite_links import FavoriteLinks
from output.database.database_base import Base, engine


class FavoriteLinksData(Base, FavoriteLinks):
    __tablename__ = "FavoriteLinks"

    id = Column(Integer, primary_key=True)
    name = Column(String(50))
    url = Column(String(50))

    @staticmethod
    def get_all_links():
        try:
            with sessionmaker(bind=engine)() as session:
                data = session.query(FavoriteLinksData).all()
                json_all_favorite_links = {}

                for favorite_link in data:
                    json_all_favorite_links[favorite_link.id] = {
                        "id": favorite_link.id,
                        "name": favorite_link.name,
                        "url": favorite_link.url,
                    }
                return json_all_favorite_links
        except Exception as e:
            logging.error(e)

    @staticmethod
    def get_favorite_link_by_id(id_favorite_link):
        try:
            with sessionmaker(bind=engine)() as session:
                return session.query(FavoriteLinksData).filter(FavoriteLinksData.id == id_favorite_link).first()
        except Exception as e:
            logging.error(e)

    def add_favorite_link(self):
        try:
            with sessionmaker(bind=engine)() as session:
                session.add(self)
                session.commit()
                logging.info("Link added")
        except Exception as e:
            logging.error(e)

    def edit_favorite_link(self):
        try:
            with sessionmaker(bind=engine)() as session:
                session.query(FavoriteLinksData).filter(FavoriteLinksData.id == self.id).update({
                    FavoriteLinksData.name: self.name,
                    FavoriteLinksData.url: self.url,
                })
                session.commit()
                logging.info("Link updated")
        except Exception as e:
            logging.error(e)

    def delete_favorite_link(self):
        try:
            with sessionmaker(bind=engine)() as session:
                session.query(FavoriteLinksData).filter(FavoriteLinksData.id == self.id).delete()
                session.commit()
                logging.info("Link deleted")
        except Exception as e:
            logging.error(e)

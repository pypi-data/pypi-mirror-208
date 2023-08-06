import logging
import hashlib
import codecs
from sqlalchemy import Column, String, Integer, Boolean
from sqlalchemy.orm import sessionmaker

from domain.user import User
from output.database.database_base import Base, engine


class UserData(Base, User):
    __tablename__ = "User"

    id = Column(Integer, primary_key=True)
    username = Column(String(50))
    password = Column(String(50))
    admin = Column(Boolean, default=False)
    change_pwd = Column(Boolean, default=False)

    @staticmethod
    def get_all():
        try:
            with sessionmaker(bind=engine)() as session:
                return session.query(UserData).all()
        except Exception as e:
            logging.error(e)

    def create(self):
        try:
            with sessionmaker(bind=engine)() as session:
                self.hash_pass()
                session.add(self)
                session.commit()
                logging.info("User added")
        except Exception as e:
            logging.error(e)

    def update(self):
        try:
            with sessionmaker(bind=engine)() as session:
                session.merge(self)
                session.commit()
                logging.info("User updated")
        except Exception as e:
            logging.error(e)

    def delete(self):
        try:
            with sessionmaker(bind=engine)() as session:
                session.delete(self.get_user_by_name(self.username))
                session.commit()
                logging.info("User deleted")
        except Exception as e:
            logging.error(e)

    def hash_pass(self):
        salt_phrase = f"$2a$12$/dskhjsd"
        hashed_password = hashlib.pbkdf2_hmac(hash_name='sha512', password=self.password.encode('utf-8'),
                                              salt=salt_phrase.encode('utf-8'), iterations=100000)
        encoded_hash = codecs.encode(hashed_password, "base64")
        self.password = encoded_hash

    @staticmethod
    def get_user_by_id(id_user):
        try:
            with sessionmaker(bind=engine)() as session:
                return session.query(UserData).filter(UserData.id == id_user).first()
        except Exception as e:
            logging.error(e)

    @staticmethod
    def get_user_by_name(name_user):
        try:
            with sessionmaker(bind=engine)() as session:
                return session.query(UserData).filter(UserData.username == name_user).first()
        except Exception as e:
            logging.error(e)

    def user_check(self):
        try:
            with sessionmaker(bind=engine)() as session:
                return session.query(UserData).filter(UserData.username == self.username).filter(
                    UserData.password == self.password).first()
        except Exception as e:
            logging.error(e)


if __name__ == "__main__":
    user = UserData(username="user1", password="us", admin=True)
    user.create()
    print(user.get_user_by_name("admin"))
'''
    if user.user_check():
        print("yes")
    else:
        print("no")
'''
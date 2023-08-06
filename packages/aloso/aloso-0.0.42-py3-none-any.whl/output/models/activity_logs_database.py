import logging

from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import sessionmaker

from domain.activity_logs import ActivityLogs
from output.database.database_base import Base, engine


class ActivityLogsData(Base, ActivityLogs):
    __tablename__ = "ActivityLogs"

    id = Column(Integer, primary_key=True)
    timestamp = Column(String(50))
    author = Column(String(50))
    action = Column(String(50))

    @staticmethod
    def get_all_activity_logs():
        try:
            with sessionmaker(bind=engine)() as session:
                data = session.query(ActivityLogsData).all()
                json_all_activity_logs = {}

                for activity_log in data:
                    json_all_activity_logs[activity_log.id] = {
                        "id": activity_log.id,
                        "timestamp": activity_log.timestamp,
                        "author": activity_log.author,
                        "action": activity_log.action,
                    }
                return json_all_activity_logs
        except Exception as e:
            logging.error(e)

    def create_activity_log(self):
        try:
            with sessionmaker(bind=engine)() as session:
                session.add(self)
                session.commit()
                logging.info("Activity log added")
        except Exception as e:
            logging.error(e)

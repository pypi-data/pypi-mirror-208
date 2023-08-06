from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base

import config

engine = create_engine(f'{config.database_resource}:///{config.database_file}')
Base = declarative_base()

import os
from sqlalchemy import create_engine, Column, Integer
from sqlalchemy.ext.declarative import declarative_base, declared_attr
from sqlalchemy.orm import sessionmaker

from . import tools

database_path = os.path.join(tools.base_path, 'database.db')
SQLALCHEMY_DATABASE_URL = f"sqlite:///{ database_path }"

engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})


class BaseModel(object):
    @declared_attr
    def __tablename__(cls):
        return cls.__name__.lower()

    def as_dict(self):
        return {c.name: getattr(self, c.name) for c in self.__table__.columns}

    id = Column(Integer, primary_key=True)


SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
BaseModelDB = declarative_base(cls=BaseModel)

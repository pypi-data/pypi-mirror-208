from abc import ABC, abstractclassmethod

from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker
from sqlalchemy.ext.declarative import declarative_base

from bfs.config import Settings


class AbstractDataBase(ABC):
    def __init__(self):
        settings = Settings()

        self.engine = create_engine(f'{settings.DATABASE_ENGINE}:' +\
            f'//{settings.DATABASE_USER}:{settings.DATABASE_PASSWORD}@' +\
                f'{settings.DATABASE_HOST}/{settings.DATABASE_NAME}')
        self.db_session = scoped_session(sessionmaker(autocommit=False,
                                                autoflush=False,
                                                bind=self.engine))
        self.Base = declarative_base()
        self.Base.query = self.db_session.query_property()

    @abstractclassmethod
    def init_db():
        """
        Import all modules here that might define models so that
        they will be registered properly on the metadata.  Otherwise
        you will have to import them first before calling init_db().
        """
        pass

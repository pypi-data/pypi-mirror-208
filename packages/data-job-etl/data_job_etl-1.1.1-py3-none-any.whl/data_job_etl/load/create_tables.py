from sqlalchemy import create_engine, inspect
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.exc import IntegrityError
import json

from data_job_etl.config.definitions import DB_STRING, DATA_PATH
from data_job_etl.config.postgres_schema import Base


def create_tables():
    engine = create_engine(DB_STRING, echo=True)

    Base.metadata.create_all(engine)



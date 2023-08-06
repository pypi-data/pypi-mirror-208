import numpy
from psycopg2.extensions import register_adapter, AsIs
from sqlalchemy import create_engine, inspect
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.exc import IntegrityError, SQLAlchemyError

from data_job_etl.config.definitions import DB_STRING
from data_job_etl.config.postgres_schema import PivottedJob, ProcessedJob, Base


def adapt_numpy_float64(numpy_float64):
    return AsIs(numpy_float64)


def adapt_numpy_int64(numpy_int64):
    return AsIs(numpy_int64)


register_adapter(numpy.float64, adapt_numpy_float64)
register_adapter(numpy.int64, adapt_numpy_int64)


class Loader:

    def __init__(self):
        self.engine = create_engine(DB_STRING, echo=True)
        self.db_session = sessionmaker(bind=self.engine)

        Base.metadata.create_all(self.engine)
        Base.metadata.bind = self.engine

    def load_processed(self, processed):
        """
        Load processed data in Postgres table.
        """
        for i in range(len(processed)):
            _id = processed.loc[i, 'id']
            url = processed.loc[i, 'url']
            title = processed.loc[i, 'title']
            company = processed.loc[i, 'company']
            stack = processed.loc[i, 'stack']
            remote = processed.loc[i, 'remote']
            location = processed.loc[i, 'location']
            industry = processed.loc[i, 'industry']
            _type = processed.loc[i, 'type']
            created_at = processed.loc[i, 'created_at']
            text = processed.loc[i, 'text']
            size = processed.loc[i, 'size']
            experience = processed.loc[i, 'experience']
            education = processed.loc[i, 'education']

            job = ProcessedJob(id=_id,
                               url=url,
                               title=title,
                               company=company,
                               stack=stack,
                               remote=remote,
                               location=location,
                               industry=industry,
                               type=_type,
                               created_at=created_at,
                               text=text,
                               size=size,
                               experience=experience,
                               education=education)

            with self.engine.connect() as connection:
                with self.db_session(bind=connection) as session:
                    session.begin()
                    try:
                        session.merge(job)
                        session.commit()
                    except SQLAlchemyError as e:
                        error = str(e.__dict__['orig'])
                        print('An exception occurred:\n', error)
                        session.rollback()

    def load_pivotted(self, pivotted):
        """
        Load pivotted data in Postgres table.
        """
        for i in range(len(pivotted)):
            raw_id = pivotted.loc[i, 'id']
            url = pivotted.loc[i, 'url']
            title = pivotted.loc[i, 'title']
            company = pivotted.loc[i, 'company']
            technos = pivotted.loc[i, 'technos']
            remote = pivotted.loc[i, 'remote']
            location = pivotted.loc[i, 'location']
            industry = pivotted.loc[i, 'industry']
            _type = pivotted.loc[i, 'type']
            created_at = pivotted.loc[i, 'created_at']
            size = pivotted.loc[i, 'size']
            experience = pivotted.loc[i, 'experience']
            education = pivotted.loc[i, 'education']

            job = PivottedJob(raw_id=raw_id,
                              url=url,
                              title=title,
                              company=company,
                              technos=technos,
                              remote=remote,
                              location=location,
                              industry=industry,
                              type=_type,
                              created_at=created_at,
                              size=size,
                              experience=experience,
                              education=education)

            with self.engine.connect() as connection:
                with self.db_session(bind=connection) as session:
                    session.begin()
                    try:
                        session.merge(job)
                        session.commit()
                    except SQLAlchemyError as e:
                        error = str(e.__dict__['orig'])
                        print('An exception occurred:\n', error)
                        session.rollback()

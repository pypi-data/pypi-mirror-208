from sqlalchemy.exc import SQLAlchemyError

from data_job_etl.config.postgres_schema import ProcessedJob
from data_job_etl.extract.extract import Extractor
from data_job_etl.transform.preprocess import Preprocessor
from data_job_etl.load.load import Loader


class UpdateTable:
    """
    Modify table once outside the automated workflow.
    """

    def __init__(self):
        self.extractor = Extractor()
        self.loader = Loader()

    def extract_processed_jobs(self):
        return self.extractor.extract_table('processed_jobs')

    def update_remote(self):
        """Modification of remote field in processed_jobs table."""
        processed_jobs = self.extract_processed_jobs()
        preprocessor = Preprocessor(processed_jobs)
        processed_jobs['remote'] = processed_jobs['remote'].apply(lambda x: preprocessor.process_remote(x))
        for i in range(len(processed_jobs)):
            _id = processed_jobs.loc[i, 'id']
            remote = processed_jobs.loc[i, 'remote']

            job = ProcessedJob(id=_id,
                               remote=remote)

            with self.loader.engine.connect() as connection:
                with self.loader.db_session(bind=connection) as session:
                    session.begin()
                    try:
                        session.merge(job)
                        session.commit()
                    except SQLAlchemyError as e:
                        error = str(e.__dict__['orig'])
                        print('An exception occurred:\n', error)
                        session.rollback()


if __name__ == "__main__":
    UpdateTable().update_remote()

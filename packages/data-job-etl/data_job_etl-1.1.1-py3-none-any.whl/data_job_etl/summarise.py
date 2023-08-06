import openai
import os
from datetime import date
from sqlalchemy.exc import SQLAlchemyError

from data_job_etl.extract.extract import Extractor
from data_job_etl.config.postgres_schema import ProcessedJob
from data_job_etl.load.load import Loader


class Summariser:
    """
    Pipeline taking a text as input and summarising it in a new column.
    """

    def __init__(self):
        self.loader = Loader()
        self.extractor = Extractor()

    def summarise(self):
        processed_jobs = self.extract_processed_jobs()
        self.load_summary(processed_jobs)

    def extract_processed_jobs(self):
        # Restrict to relevant data engineer jobs
        query = 'SELECT id, text ' \
                'FROM processed_jobs ' \
                "WHERE title ~* '.*(data|analytics|devops|cloud).*(engineer|ingénieur).*|.*(engineer|ingénieur).*(data|données|big data|bigdata)|.*etl.*' " \
                'AND summary is null ' \
                'ORDER BY created_at DESC;'
        processed_jobs = self.extractor.extract_query(query)
        return processed_jobs

    @staticmethod
    def request_gpt(text):
        api_key = os.getenv('OPENAI_API_KEY')
        openai.api_key = api_key
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "user",
                 "content": f"Please provide a summary for this job description in less than 50 "
                            f"words and by emphasizing on the skills: {text}"}
            ]
        )
        summary = response.choices[0].message.content
        return summary

    def load_summary(self, processed_jobs):
        for i in range(len(processed_jobs)):
            # Prompt gpt-3.5-turbo
            summary = self.request_gpt(processed_jobs['text'][i])

            # Select new fields to update table
            _id = processed_jobs['id'][i]
            job = ProcessedJob(id=_id,
                               summary=summary)

            # Update id and summary in database
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


if __name__ == '__main__':
    Summariser().summarise()

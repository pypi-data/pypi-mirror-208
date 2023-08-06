from sqlalchemy import create_engine
import pandas as pd

from data_job_etl.config.definitions import DB_STRING


class Extractor:

    def __init__(self):
        self.engine = create_engine(DB_STRING)

    def extract_table(self, table):
        jobs = pd.read_sql(table, self.engine)
        return jobs

    def extract_query(self, query):
        jobs = pd.read_sql_query(query, self.engine)
        return jobs


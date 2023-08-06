import pandas as pd
import numpy as np
import re
from pathlib import Path
from sqlalchemy import create_engine
from datetime import datetime
from sqlalchemy.exc import SQLAlchemyError


from data_job_etl.config.etl_logger import logger
from data_job_etl.config.definitions import DB_STRING
from data_job_etl.config.postgres_schema import RankedJob
from data_job_etl.extract.extract import Extractor
from data_job_etl.load.load import Loader

pd.set_option('display.max_rows', 500)


class Ranker:

    def __init__(self):
        self.logger = logger
        self.loader = Loader()
        self.extractor = Extractor()

    def rank(self):
        to_rank = self.extract_relevant_data()
        to_rank['remote_num'] = to_rank['remote'].apply(lambda x: self.numerise_remote(x))
        to_rank['exp_num'] = to_rank.apply(self.numerise_experience, axis=1)
        ranked = self.compute_cosine_similarity(original=to_rank)
        self.load_rank(ranked)
        # self.output_csv(ranked)

    def extract_relevant_data(self):
        query = "SELECT * FROM relevant;"
        relevant_jobs = self.extractor.extract_query(query)
        return relevant_jobs

    @staticmethod
    def numerise_remote(row):
        if 'total' in row:
            return 3
        elif 'partiel' in row:
            return 2
        elif 'ponctuel' in row:
            return 1
        else:
            return 0

    @staticmethod
    def numerise_experience(x):
        if re.search(r'[jJ]unior', x['title']) or x['experience'] == '< 6 mois':
            return 3
        elif x['experience'] == ('> 6 mois' or '> 1 an' or '> 2 ans'):
            return 2
        elif x['experience'] == ('> 3 ans' or '> 4 ans' or '> 5 ans' or '> 7 ans' or '> 10 ans'):
            return 0
        else:
            return 1

    @staticmethod
    def compute_cosine_similarity(original):
        # Define matrix where each row represents a document and each column a feature (remote, junior)
        docs = original[['id', 'remote_num', 'exp_num']].set_index('id').to_numpy()
        # Define the query as a vector with the same number of features as the documents
        numerised_ideal = np.array([3, 3])
        # Multiply the document matrix by the weight matrix to get the weighted document matrix
        weights = np.array([1, 1])
        weighted_docs = docs * weights
        # Multiply the query vector by the weight vector to get the weighted query vector
        weighted_query = numerised_ideal * weights
        # Compute the cosine similarity between the query and each document
        similarities = np.dot(weighted_docs, weighted_query) / (
                    np.linalg.norm(weighted_docs) * np.linalg.norm(weighted_query))
        # Rank the documents based on their similarity scores
        ranked_docs = [(score, i + 1) for i, score in enumerate(similarities)]
        # Transform back into a series
        ranked_docs_only = map(lambda x: x[0], ranked_docs)
        ranked_docs_only_s = pd.Series(ranked_docs_only).rename('rank')
        # Merge with original dataframe
        ranked = pd.merge(original, ranked_docs_only_s, left_index=True, right_index=True, suffixes=('_x', ''))
        ranked.drop(columns='rank_x', inplace=True)
        # Return with higher ranks at the top
        return ranked.sort_values(by='rank', ascending=False)

    @staticmethod
    def output_csv(df):
        filepath = Path(__file__).parent / 'data' / f'ranked_jobs_{datetime.now().strftime("%d-%m")}.csv'
        df.to_csv(filepath)

    def load_rank(self, ranked):
        for i in range(len(ranked)):
            _id = ranked.loc[i, 'id']
            rank = ranked.loc[i, 'rank']
            remote_num = ranked.loc[i, 'remote_num']
            exp_num = ranked.loc[i, 'exp_num']

            job = RankedJob(job_id=_id,
                            rank=rank,
                            remote_num=remote_num,
                            exp_num=exp_num)

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
    Ranker().rank()

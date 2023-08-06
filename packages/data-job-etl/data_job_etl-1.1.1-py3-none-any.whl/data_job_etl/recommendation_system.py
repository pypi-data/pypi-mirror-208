import os
import pandas as pd
import numpy as np
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from sqlalchemy import create_engine

USER = os.getenv('JOB_MARKET_DB_USER')
PWD = os.getenv('JOB_MARKET_DB_PWD')

pd.options.mode.chained_assignment = None
pd.reset_option('display.max_rows')
pd.set_option('display.max_rows', 500)


def extract_data():
    engine = create_engine(f"postgresql://{USER}:{PWD}@localhost:5432/job_market")
    query = 'SELECT * FROM relevant;'
    relevant = pd.read_sql_query(query, engine)
    relevant = relevant[
        ['id', 'title', 'company', 'remote', 'location', 'stack', 'education', 'size', 'experience', 'rank', 'url',
         'industry', 'type', 'created_at', 'text', 'summary']]
    # print(relevant.info())

    user_df = relevant[['id']]
    item_df = relevant[['id', 'title', 'company', 'remote', 'stack']]
    df = pd.merge(user_df, item_df, on='id')
    return df


def fill_na_features(df):
    features = ['title', 'remote', 'location', 'stack', 'education', 'size', 'experience', 'text']
    for feature in features:
        df[feature] = df[feature].fillna('')


def strip_stack(row):
    new_row = row['stack'].replace('{', '').replace('}', '').split(',')
    return new_row


def combine_features(row):
    new_row = row['title'] + ' ' + row['remote']
    for w in row['stack_2']:
        new_row = new_row + ' ' + w
    return new_row


def extract_features(df):
    cv = CountVectorizer()
    count_matrix = cv.fit_transform(df["combined_features"])
    print("Count Matrix:\n", count_matrix.toarray())
    print("Count Matrix:\n", count_matrix.toarray().shape)
    return count_matrix


def get_index_from_id(df, _id):
    return df[df.id == _id].index


def get_title_from_index(df, index):
    return df[df.index == index]["title"].values[0]


def get_row_from_index(df, index):
    return df[df.index == index]


def find_similar_jobs(df, job_id, cosine_sim):
    job_index = get_index_from_id(df, job_id)[0]
    similar_jobs = list(enumerate(cosine_sim[job_index]))
    sorted_similar_jobs = sorted(similar_jobs, key=lambda x: x[1], reverse=True)
    similar_jobs = [get_row_from_index(df, job[0]) for job in sorted_similar_jobs]
    return similar_jobs


def main():
    # Prepare data
    df = extract_data()
    fill_na_features(df)
    df['stack_2'] = df.apply(strip_stack, axis=1)
    df["combined_features"] = df.apply(combine_features, axis=1)

    # Calculate cosine similarity
    count_matrix = extract_features(df)
    cosine_sim = cosine_similarity(count_matrix)
    print(cosine_sim)

    # Define the list of job IDs we like
    job_ids = [56987, 56988]

    # Find similar jobs
    i = 0
    for job_id in job_ids:
        similar_jobs = find_similar_jobs(df, job_id, cosine_sim)
        print(f"Similar jobs for Job ID {job_id}:")
        for job in similar_jobs:
            print(job)
            i = i + 1
            if i > 15:
                break


if __name__ == '__main__':
    main()

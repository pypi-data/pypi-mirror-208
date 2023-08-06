import os
from pathlib import Path

PROJECT_PATH = Path(os.path.dirname(os.path.abspath(__file__))).parent
DATA_PATH = os.path.join(PROJECT_PATH, 'elt/transform/data')

JOB_MARKET_DB_PWD = os.environ['JOB_MARKET_DB_PWD']
JOB_MARKET_DB_USER = os.environ['JOB_MARKET_DB_USER']
DB_STRING = f"postgresql://{JOB_MARKET_DB_USER}:{JOB_MARKET_DB_PWD}@localhost:5432/job_market"


import json


class TechnoBuilder:
    
    def build_all_technos(self):
        with open('/Users/donor/PycharmProjects/data-job-etl/data_job_etl/data/mad2023.json', 'r') as f:
            mad = json.load(f)
        
        mad_technos = [x['name'] for x in mad]
        other_technos = {'DataBuildTool', 'MxNet', 'Hadoop', 'Beam', 'BigQuery', 'Pig', 'DataStudio', 'Redshift', 'Shell',
                         'Gitlab', 'data vault', 'Ceph', 'Airflow', 'GCP', 'IAM', 'k8s', 'Numpy', 'MAPR', 'Node', 'Athena',
                         'Unix', 'NiFi', 'Mongo', 'NoSQL', 'Unix Shell', 'Azure', 'Go', 'Golang', 'Perl', 'EC2', 'EMR', 'SPAR',
                         'Jenkins', 'Git', 'C/C\\+\\+', 'airflow', 'CloudSQL', 'Ruby', 'Redshift Spectrum', 'Glue', 'Postgres',
                         'Salt', 'python', 'nodejs', 'Go lang', 'Qlikview', 's3', 'Protobuf', 'MapReduce', 'Google Cloud',
                         'Elasticsearch', 'Spark', 'Celery', 'Pagerduty', 'mlflow', 'React', 'C\\+\\+', 'Tensorflow',
                         'Stitch DataGraphQL', 'Django', 'HDFS', 'Matillion WTL', 'SQL server', 'Istio', 'Dataflow', 'Codecov', 
                         'UNIX', 'Typescript', 'DynamoDB', 'Vitess', 'Cassandra', 'HTTP', 'VizQL', 'C#', 'S3', 'SQL', 'Akka',
                         'MS-SQL', 'Stackdriver', 'Quicksilver', 'Github', 'dbt', 'DAX', 'StitchData', 'HBase',
                         'Microsoft SSIS', 'AWS S3', 'K8S', 'Java', 'SparkSQL', 'Kubeflow', 'ElasticSearch', '(No)SQL',
                         'Kinesis', 'Bigtable', 'CockroachDB', 'Scipy', 'Bash', 'git', 'Scikit Learn', 'Google Cloud Platform',
                         'Synapse', 'AWS', 'Spanner', 'H20', 'Javascript', 'LAMP', 'SQL Server', 'Py torch', 'PHP', 'PowerBI',
                         'gRPC', 'SAP', 'Neo4J', 'Cloud SQL', 'Reddis', 'Linux', 'SageMaker', 'dataiku', 'PQL', 'GCS',
                         'CircleCI', 'Kimball'}
        all_technos = other_technos.union(mad_technos)

        return all_technos

    def define_personal_skills(self):
        PROFICIENCY_LEVELS = {
            'never used': 0,
            'already used': 1,
            'used multiple times': 2,
            'used a lot': 3
        }

        MY_MAD2023 = {
            'S3': 2,
            'Redshift': 1,
            'Kinesis': 1,
            'DynamoDB': 1,
            'MongoDB': 1,
            'Neo4j': 1,
            'dbt': 0,
            'Glue': 1,
            'Cloudwatch': 1,
            'Lambda': 1,
            'HDFS': 1,
            'Spark': 1,
            'MapReduce': 1,
            'YARN': 1,
            'Kubernetes': 1,
            'Docker': 2,
            'Hive': 1,
            'PostgreSQL': 3,
            'MySQL': 1,
            'Cassandra': 1,
            'Hbase': 1,
            'Airflow': 3,
            'Zookeeper': 1,
            'Spark Streaming': 1,
            'Kafka': 1,
            'Python': 3,
            'R': 2,
            'numpy': 3,
            'pandas': 3,
            'SciPy': 1,
            'R Studio': 2,
            'tidyverse': 2,
            'Scikit-learn': 2,
            'OpenAI GPT3': 2,
            'Elastic': 1,
            'D3': 1,
            'matplotlib': 3,
            'seaborn': 1,
            'bokeh': 1,
            'ggplot2': 2,
            'jupyter': 3,
            'OpenStreetMap': 1
        }

        MY_OTHER_SKILLS = {
            'shiny',
            'pytest',
            'scrapy',
            'boto3',
        }

        MY_COURSES = {

        }


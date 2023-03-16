from airflow.decorators import dag, task, task_group

import pendulum
import os
import sys

sys.path.append(f'{os.getcwd()}/dags')

from Classes.Parser import ProteinParser
from Classes.Neo4jDBConnector import Neo4jDBConnector

@dag(schedule=None, start_date=pendulum.datetime(2021, 1, 1, tz="UTC"), catchup=False)
def protein_pipeline():
    file_path = f'{os.getcwd()}/dags/data/Q9Y261.xml'
    with open(file_path, 'r') as f:
        data = f.read()

    @task()
    def extract():
        protein_parser = ProteinParser(data)
        return protein_parser.get_protein_data()
    
    @task()
    def load(data: dict):
        uri = "bolt://host.docker.internal:7687"
        user = "superman"
        password = "testing123"
        neo4j = Neo4jDBConnector(uri, user, password)
        neo4j.load_protein_data(data)

    load(extract())

pipeline = protein_pipeline()
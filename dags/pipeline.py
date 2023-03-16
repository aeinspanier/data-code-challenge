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
    
    def load(data: dict):
        pass

    extract()

pipeline = protein_pipeline()
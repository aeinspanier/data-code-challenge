from airflow.decorators import dag, task, task_group

import pendulum
import os
import sys

sys.path.append(f'{os.getcwd()}/dags')

from Classes.Parser import ProteinParser
from Classes.Neo4jDBConnector import Neo4jDBConnector

@dag(schedule=None, start_date=pendulum.datetime(2021, 1, 1, tz="UTC"), catchup=False)
def protein_pipeline():
    ## [USER DEFINED VALUE] ##
    file_name = 'Q9Y261.xml'
    ## [USER DEFINED VALUE] ##
    
    file_path = f'{os.getcwd()}/dags/data/{file_name}'
    with open(file_path, 'r') as f:
        data = f.read()

    @task()
    def extract():
        protein_parser = ProteinParser(data)
        return protein_parser.get_protein_data()
    
    @task()
    def load(data: dict):
        ## [USER DEFINED VALUES] ##
        uri = "bolt://host.docker.internal:7687"
        user = "superman"
        password = "testing123"
        ## [USER DEFINED VALUES] ##
        neo4j = Neo4jDBConnector(uri, user, password)
        neo4j.load_protein_data(data)

    load(extract())

pipeline = protein_pipeline()
from airflow.decorators import dag, task, task_group

import pendulum

from bs4 import BeautifulSoup

@dag(schedule=None, start_date=pendulum.datetime(2021, 1, 1, tz="UTC"), catchup=False)
def protein_pipeline():
    @task(task_id="get-xml-file-data", retries=2)
    def get_xml_data():
        file_path = "./data/Q9Y261.xml"
        from bs4 import BeautifulSoup
        with open(file_path, 'r') as f:
            data = f.read()
        return BeautifulSoup(data, 'xml')

    @task()
    def extract_full_names(file_data: BeautifulSoup):
        full_names = file_data.find_all('fullName')
        return list(map(lambda ele: ele.text, full_names))

    @task()
    def extract_protein(file_data: BeautifulSoup):
        return file_data.find('accession').text
    
    @task()
    def extract_organism(file_data: BeautifulSoup):
        organism_ref = file_data.find('organism')
        name = organism_ref.find('name', {'type': 'scientific'}).text
        id = organism_ref.find('dbReference', {'type':'NCBI Taxonomy'}).get('id')
        return {'name': name, 'id': id}
    
    @task()
    def extract_references(file_data: BeautifulSoup):
        def parse_reference(reference: BeautifulSoup):
            citation_node = reference.find('citation')
            type = citation_node.get('type')
            pubmed_ref = reference.find('dbReference', {'type':'PubMed'})
            doi_ref = reference.find('dbReference', {'type':'DOI'})
            id_pubmed = pubmed_ref.get('id') if pubmed_ref is not None else None
            id_doi = doi_ref.get('id') if doi_ref is not None else None
            name = citation_node.get('name')
            authors = list(map(lambda ele: ele.get('name'), reference.find('authorList').find_all('person')))
            return {
                'id_pubmed': id_pubmed,
                'id_doi': id_doi,
                'type': type,
                'name': name,
                'authors': authors
            }
        references = file_data.find_all('reference')
        return list(map(parse_reference, references))
    
    @task()
    def extract_features(file_data: BeautifulSoup):
        def parse_feature(feature: BeautifulSoup):
            location = feature.find('location')
            position = location.find('position')
            begin = location.find('begin')
            end = location.find('end')
            return {
                'name': feature.get('description'),
                'type': feature.get('type'),
                'position': position.get('position') if position is not None else None,
                'begin_position': begin.get('position') if begin is not None else None,
                'end_position': end.get('position') if end is not None else None,
            }
        features = file_data.find_all('feature')
        return list(map(parse_feature, features))
    
    @task()
    def extract_genes(file_data: BeautifulSoup):
        def parse_gene(gene: BeautifulSoup):
            return {
                'name': gene.text,
                'status': gene.get('type')
            }
        genes = file_data.find('gene').find_all('name')
        return list(map(parse_gene, genes))
        
    @task_group
    def extract_data(file_data: BeautifulSoup):
        return {
            "protein": extract_protein(file_data),
            "full_names": extract_full_names(file_data),
            "organism": extract_organism(file_data),
            "references": extract_references(file_data),
            "features": extract_features(file_data),
            "genes": extract_genes(file_data)
        }

    @task()
    def load(values: dict):
        print(
            f"""{values}"""
        )

    load(extract_data(get_xml_data()))

pipeline = protein_pipeline()
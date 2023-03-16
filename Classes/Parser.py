from bs4 import BeautifulSoup

class ProteinParser():
    def __init__(self, data_file):
        self.soup = BeautifulSoup(data_file, 'xml')
        
    def get_protein_data(self):
        return {
            "protein": self.extract_protein(),
            "organism": self.extract_organism(),
            "references": self.extract_references(),
            "features": self.extract_features(),
            "genes": self.extract_genes(),
            "full_names": self.extract_full_names()
        }
    
    def extract_full_names(self):
        full_names = self.soup.find_all('fullName')
        return list(map(lambda ele: ele.text, full_names))

    def extract_protein(self):
        return self.soup.find('accession').text
    
    def extract_organism(self):
        organism_ref = self.soup.find('organism')
        name = organism_ref.find('name', {'type': 'scientific'}).text
        id = organism_ref.find('dbReference', {'type':'NCBI Taxonomy'}).get('id')
        return {'name': name, 'id': id}
    
    def extract_references(self):
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
        references = self.soup.find_all('reference')
        return list(map(parse_reference, references))
    
    def extract_features(self):
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
        features = self.soup.find_all('feature')
        return list(map(parse_feature, features))
    
    def extract_genes(self):
        def parse_gene(gene: BeautifulSoup):
            return {
                'name': gene.text,
                'status': gene.get('type')
            }
        genes = self.soup.find('gene').find_all('name')
        return list(map(parse_gene, genes))
    
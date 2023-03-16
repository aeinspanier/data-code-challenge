from neo4j import GraphDatabase
import logging
from neo4j.exceptions import ServiceUnavailable

class Neo4jDBConnector():
    def __init__(self, uri, user, password):
        self.driver = GraphDatabase.driver(uri, auth=(user, password))

    def close(self):
        # Don't forget to close the driver connection when you are finished with it
        self.driver.close()

    def load_protein_data(self, data):
        with self.driver.session(database="neo4j") as session:
            # First, we create the protein
            protein_id = data.get('protein')
            organism = data.get('organism')
            full_names = data.get('full_names')
            references = data.get('references')
            features = data.get('features')
            genes = data.get('genes')
            
            
            result = session.execute_write(self._create_protein, protein_id)
            print(f"Created protein {result[0]}")
            
            result = session.execute_write(self._create_organism_relationship,
                                            protein_id, organism.get('name'), organism.get('id'))
            for row in result:
                print(f"created organism: {row.get('o')} for protein {row.get('p')}")
            
            for fn in full_names:
                result = session.execute_write(self._create_full_name_relationship,
                                            protein_id, fn)
                for row in result:
                    print(f"created full name: {row.get('fn')} for protein {row.get('p')}")
                
            
            for ref in references:
                result = session.execute_write(self._create_reference_relationship,
                                            protein_id, ref.get('id_pubmed'), ref.get('id_doi'), 
                                            ref.get('type'), ref.get('name'))
                for row in result:
                    print(f"created reference: {row.get('ref')} for protein {row.get('p')}")
                
                authors = ref.get('authors')
                if authors:
                    for author in authors:
                        result = session.execute_write(self._create_author_relationship,
                                            protein_id, ref.get('name'), author)
                        for row in result:
                            print(f"created author: {row.get('a')} for reference {row.get('ref')} for protein {row.get('p')}")
            
            for feat in features:
                result = session.execute_write(self._create_feature_relationship,
                                            protein_id, feat.get('name'), feat.get('type'), feat.get('position'),
                                            feat.get('begin_position'), feat.get('end_position'))
                for row in result:
                    print(f"created feature: {row.get('f')} for protein {row.get('p')}")
            
            for gene in genes:
                result = session.execute_write(self._create_gene_relationship,
                                            protein_id, gene.get('name'), gene.get('status'))
                for row in result:
                    print(f"created gene: {row.get('g')} for protein {row.get('p')}")
              
    @staticmethod
    def _create_protein(tx, protein_id):
        query = (
            "CREATE (p:Protein { id: $protein_id }) "
            "RETURN p"
        )
        result = tx.run(query, protein_id=protein_id)
        try:
            return [row["p"]["id"] for row in result]
        # Capture any errors along with the query and data for traceability
        except ServiceUnavailable as exception:
            logging.error("{query} raised an error: \n {exception}".format(
                query=query, exception=exception))
            raise
    
    @staticmethod
    def _create_organism_relationship(tx, protein_id, organism_name, taxonomy_id):
        query = (
            "MATCH (p:Protein { id: $protein_id })"
            "CREATE (o:Organism { name: $organism_name, taxonomy_id: $taxonomy_id }) "
            "CREATE (p)-[:IN_ORGANISM]->(o) "
            "RETURN p, o"
        )
        result = tx.run(query, protein_id=protein_id, organism_name=organism_name, taxonomy_id=taxonomy_id)
        try:
            return [{"p": row["p"]["id"], "o": row["o"]["name"]} for row in result]
        # Capture any errors along with the query and data for traceability
        except ServiceUnavailable as exception:
            logging.error("{query} raised an error: \n {exception}".format(
                query=query, exception=exception))
            raise
    
    @staticmethod
    def _create_full_name_relationship(tx, protein_id, full_name):
        query = (
            "MATCH (p:Protein { id: $protein_id })"
            "CREATE (fn:FullName { name: $full_name })"
            "CREATE (p)-[:HAS_FULL_NAME]->(fn)"
            "RETURN p, fn"
        )
        result = tx.run(query, protein_id=protein_id, full_name=full_name)
        try:
            return [{"p": row["p"]["id"], "fn": row["fn"]["name"]} for row in result]
        # Capture any errors along with the query and data for traceability
        except ServiceUnavailable as exception:
            logging.error("{query} raised an error: \n {exception}".format(
                query=query, exception=exception))
            raise
    
    @staticmethod
    def _create_reference_relationship(tx, protein_id, ref_id_pubmed, ref_id_doi, ref_type, ref_name):
        query = (
            "MATCH (p:Protein { id: $protein_id })"
            "CREATE (ref:Reference { id_pubmed: $ref_id_pubmed, id_doi: $ref_id_doi, type: $ref_type, name: $ref_name })"
            "CREATE (p)-[:HAS_REFERENCE]->(ref)"
            "RETURN p, ref"
        )
        result = tx.run(query, protein_id=protein_id, ref_id_pubmed=ref_id_pubmed, 
                        ref_id_doi=ref_id_doi, ref_type=ref_type, ref_name=ref_name)
        try:
            return [{"p": row["p"]["id"], "ref": row["ref"]["name"]} for row in result]
        # Capture any errors along with the query and data for traceability
        except ServiceUnavailable as exception:
            logging.error("{query} raised an error: \n {exception}".format(
                query=query, exception=exception))
            raise
    
    @staticmethod
    def _create_author_relationship(tx, protein_id, ref_name, author):
        query = (
            "MATCH (p:Protein { id: $protein_id}) -- (ref:Reference { name: $ref_name })"
            "CREATE (a:Author { name: $author })"
            "CREATE (ref)-[:HAS_AUTHOR]->(a)"
            "RETURN p, ref, a"
        )
        result = tx.run(query, protein_id=protein_id, ref_name=ref_name, author=author)
        try:
            return [{"p": row["p"]["id"], "ref": row["ref"]["name"], "a": row['a']['name']} for row in result]
        # Capture any errors along with the query and data for traceability
        except ServiceUnavailable as exception:
            logging.error("{query} raised an error: \n {exception}".format(
                query=query, exception=exception))
            raise
    
    @staticmethod
    def _create_feature_relationship(tx, protein_id, feat_name, feat_type, feat_position,
                                            feat_begin_position, feat_end_position):
        query = (
            "MATCH (p:Protein { id: $protein_id})"
            "CREATE (f:Feature { name: $feat_name, type: $feat_type  })"
            "CREATE (p)-[:HAS_FEATURE { position: $feat_position, begin_position: $feat_begin_position, end_position: $feat_end_position} ]->(f)"
            "RETURN p, f"
        )
        result = tx.run(query, protein_id=protein_id, feat_name=feat_name, feat_type=feat_type, feat_position=feat_position,
                                            feat_begin_position=feat_begin_position, feat_end_position=feat_end_position)
        try:
            return [{"p": row["p"]["id"], "f": row["f"]["name"]} for row in result]
        # Capture any errors along with the query and data for traceability
        except ServiceUnavailable as exception:
            logging.error("{query} raised an error: \n {exception}".format(
                query=query, exception=exception))
            raise
    
    @staticmethod
    def _create_gene_relationship(tx, protein_id, name, status):
        query = (
            "MATCH (p:Protein { id: $protein_id})"
            "CREATE (g:GENE { name: $name })"
            "CREATE (p)-[:FROM_GENE { status: $status} ]->(g)"
            "RETURN p, g"
        )
        result = tx.run(query, protein_id=protein_id, name=name, status=status)
        try:
            return [{"p": row["p"]["id"], "g": row["g"]["name"]} for row in result]
        # Capture any errors along with the query and data for traceability
        except ServiceUnavailable as exception:
            logging.error("{query} raised an error: \n {exception}".format(
                query=query, exception=exception))
            raise

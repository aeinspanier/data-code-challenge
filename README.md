## Application Information
This is an application for loading protein data locally from .xml files to a Neo4j graph database. The tech stack is Airflow, Docker, and Python based.

## Data Model
The data model should be a graph data model. The graph should contain nodes for proteins, genes, organisms, references, and more. The graph should contain edges for the relationships between these nodes. The relationships should be based on the XML schema. For example, the `protein` element contains a `recommendedName` element. The `recommendedName` element contains a `fullName` element. The `fullName` element contains the full name of the protein. The graph should contain an edge between the `protein` node and the `fullName` node.

Here is an example for the target data model:

![Example Data Model](./img/example_data_model.png)


## Environment Setup
Required dependencies include:

1. Item
2. Item

[1]: http://example.com/ "Title"
[2]: http://example.org/ "Title"


## Example Code
In the `example_code` directory, you will find some example Python code for loading data to Neo4j.

## Andrew Notes

Docker image was too tricky to get to work.
So I just used the destop version. Created a new database, then created a new user within the DB with username = superman, password = testing123
followed this guide: https://towardsdatascience.com/neo4j-cypher-python-7a919a372be7

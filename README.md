## Application Information
This is an application for loading protein data locally from .xml files to a Neo4j graph database. The tech stack is Airflow, Docker, and Python based.

## Data Model
The data model should be a graph data model. The graph should contain nodes for proteins, genes, organisms, references, and more. The graph should contain edges for the relationships between these nodes. The relationships should be based on the XML schema. For example, the `protein` element contains a `recommendedName` element. The `recommendedName` element contains a `fullName` element. The `fullName` element contains the full name of the protein. The graph should contain an edge between the `protein` node and the `fullName` node.

Here is an example for the target data model:

![Example Data Model](./img/example_data_model.png)


## Environment Setup
Required dependencies include:

1. [Docker Desktop](https://www.docker.com/products/docker-desktop/)
2. [Neo4j Desktop](https://neo4j.com/download/)

The first step is to create a python virtual environment. [VSCode offers a nice way to do this](https://code.visualstudio.com/docs/python/environments), Otherwise the following commands should work too.  

```
python -m venv .venv
pip install -r requirements.txt
```  

Next, we will set up Airflow. We will be using the `docker-compose.yml` file provided by [Airflow](https://airflow.apache.org/docs/apache-airflow/stable/howto/docker-compose/index.html)

However, the yaml file has been modified slightly to include an extended version of airflow that we will set up with a separate Dockerfile, in order to install the Neo4j driver dependencies to the airflow environment:  

```
x-airflow-common:
  &airflow-common
  ...
  image: ${AIRFLOW_IMAGE_NAME:-extended_airflow:latest}
  ...
```

Start docker destop, and run the following commands:  

1. Builds the extended airflow container.
```
docker build . --tag extended_airflow:latest 
```
2. Initializes Airflow.
```
docker-compose up airflow-init
```
3. Starts Airflow on localhost:8080
```
docker-compose up
```

Once all of that is done, navigate to `localhost:8080` and log into airflow with username and password both being `airflow`

Next, if it's your first time setting up Neo4j locally, follow [this guide](https://towardsdatascience.com/neo4j-cypher-python-7a919a372be7) to create a new project and a user. Default user credentials used in the app are `username: superman, password: testing123` - but you can choose whatever you like. Just make sure to update the credentials in the `dags/pipeline.py` file:

```
@task()
    def load(data: dict):
        ## [USER DEFINED VALUES] ##
        uri = "bolt://host.docker.internal:7687"
        user = "superman"
        password = "testing123"
        ## [USER DEFINED VALUES] ##
        ...
```

Make sure Neo4j is running on port 7687 as well.

The default data that the pipeline will extract is included in the repository (`Q9Y261.xml`). However, if you would like to process a different file, place it in the `data/` folder and change the filename in `dags/pipeline.py`:

```
@dag(schedule=None, start_date=pendulum.datetime(2021, 1, 1, tz="UTC"), catchup=False)
def protein_pipeline():
    ## [USER DEFINED VALUE] ##
    file_name = 'Q9Y261.xml'
    ## [USER DEFINED VALUE] ##
```

## Running the Pipeline:

Once the environment has been configured, the pipeline is ready to run. In the airflow UI, navigate to `protein_pipeline` dag and run it. Once it completes, you should be able to navigate to the Neo4j DB and see the data loaded via executing:

```
MATCH (n)
RETURN n
```

## Shutdown

To kill the airflow containers, run the following command:

```
docker compose down --volumes --rmi all
```



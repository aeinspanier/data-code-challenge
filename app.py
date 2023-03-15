from airflow.models import DAG
from airflow.operators.python import PythonOperator

from datetime import datetime

from dags.pipeline import run_pipeline

with DAG(
    dag_id='protein_pipeline_dag',
    start_date=datetime(2021, 1, 1),
    schedule_interval=None
) as dag:
    run_this = PythonOperator(
        task_id='run_pipeline',
        provide_context=True,
        python_callable=run_pipeline,
        dag=dag,
    )

run_this
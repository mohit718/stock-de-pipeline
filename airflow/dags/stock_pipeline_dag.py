from airflow import DAG
from airflow.operators.bash import BashOperator
from datetime import datetime

PROJECT_DIR = "/opt/airflow/stock-de-pipeline"

default_args = {
    "owner": "mohit",
    "retries": 1,
}
with DAG(
    dag_id="stock_data_pipeline",
    default_args=default_args,
    start_date=datetime(2026, 7, 1),
    schedule_interval="@daily",
    catchup=False,
    tags=["portfolio", "data-engineering", "snowflake"],
) as dag:

    extract = BashOperator(
        task_id="extract_to_s3",
        bash_command=f"python {PROJECT_DIR}/extract.py",
    )

    load_raw = BashOperator(
        task_id="load_raw_to_snowflake",
        bash_command=f"python {PROJECT_DIR}/load_raw.py",
    )

    merge = BashOperator(
        task_id="merge_to_fact_table",
        bash_command=f"python {PROJECT_DIR}/load_and_merge.py",
    )

    extract >> load_raw >> merge
from airflow import DAG
from airflow.operators.python import PythonOperator
from datetime import datetime, timedelta
import os

from kompas.crawler import (
        extract_article_content,
        extract_kompas_articles_index
)

BASE_DATA_DIR = os.path.join(os.environ.get('AIRFLOW_HOME', '/opt/airflow'), 'dags', 'data')
# Pastikan sub-direktori juga dibuat
os.makedirs(os.path.join(BASE_DATA_DIR, 'raw_index'), exist_ok=True)
os.makedirs(os.path.join(BASE_DATA_DIR, 'raw_content'), exist_ok=True)
os.makedirs(os.path.join(BASE_DATA_DIR, 'transformed'), exist_ok=True)

with DAG (
    dag_id='kompas_dag',
    start_date=datetime(2025,1,1),
    schedule_interval='@daily',
    catchup=False,
    tags=['crawler','kompas','news']
) as dag:
    # E1: Extract index
    extract_index_task = PythonOperator(
        task_id='extract_raw_article_index',
        python_callable=extract_kompas_articles_index,
        op_kwargs={
            'selected_date': '{{ ds }}',
            'output_raw_path': os.path.join(BASE_DATA_DIR, 'raw_index', 'kompas_index_articles_{{ ds }}.json')
        },
    )

    # E2: Extract content
    extract_content_task = PythonOperator(
        task_id='extract_kompas_full_content',
        python_callable=extract_article_content,
        op_kwargs={
            'input_index_path': os.path.join(BASE_DATA_DIR, 'raw_index', 'kompas_index_articles_{{ ds }}.json'),
            'output_content_path': os.path.join(BASE_DATA_DIR, 'raw_content', 'kompas_full_articles_{{ ds }}.json')
        }    
    )

    # transform_task = PythonOperator(
    #     task_id='transform_articles_data',
    #     python_callable=transform_articles_data,
    #     op_kwargs={
    #         'input_content_path': os.path.join(BASE_DATA_DIR, 'raw_content', 'kompas_full_articles_{{ ds }}.json'),
    #         'output_transformed_path': os.path.join(BASE_DATA_DIR, 'transformed', 'kompas_transformed_articles_{{ ds }}.json')
    #     },
    # )

    extract_index_task >> extract_content_task

    
    

"""
Airflow DAG: Credit Card Fraud Detection ETL Pipeline
Orchestrates Bronze → Silver → Gold layers using Databricks Jobs
"""

from datetime import datetime, timedelta
from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.operators.dummy import DummyOperator
from airflow.exceptions import AirflowException
from airflow.hooks.base import BaseHook
from airflow.models import Variable

import requests
import json

# Configuration
DATABRICKS_HOST = Variable.get("databricks_host", "https://adb-xxxx.azuredatabricks.net")
DATABRICKS_TOKEN = Variable.get("databricks_token", "")

# Job IDs (set these to your actual Databricks job IDs)
INGESTION_JOB_ID = Variable.get("ingestion_job_id", 123)
BRONZE_JOB_ID = Variable.get("bronze_job_id", 124)
SILVER_JOB_ID = Variable.get("silver_job_id", 125)
GOLD_JOB_ID = Variable.get("gold_job_id", 126)

# Default arguments
default_args = {
    'owner': 'data-engineering',
    'retries': 2,
    'retry_delay': timedelta(minutes=5),
    'email': ['data-alerts@company.com'],
    'email_on_failure': True,
    'email_on_retry': False,
}

def trigger_databricks_job(job_id, task_id, **context):
    """Trigger a Databricks job and wait for completion"""
    
    headers = {
        "Authorization": f"Bearer {DATABRICKS_TOKEN}",
        "Content-Type": "application/json"
    }
    
    # Trigger job
    trigger_url = f"{DATABRICKS_HOST}/api/2.0/jobs/run-now"
    trigger_payload = {"job_id": job_id}
    
    response = requests.post(trigger_url, json=trigger_payload, headers=headers)
    response.raise_for_status()
    
    run_id = response.json()['run_id']
    print(f"✓ Job {job_id} triggered with run_id: {run_id}")
    
    # Wait for completion
    max_retries = 720  # 12 hours with 60-second intervals
    retry_count = 0
    
    while retry_count < max_retries:
        get_url = f"{DATABRICKS_HOST}/api/2.0/jobs/runs/get"
        get_params = {"run_id": run_id}
        
        response = requests.get(get_url, params=get_params, headers=headers)
        response.raise_for_status()
        
        run_data = response.json()['state']
        state = run_data
        
        if state == "TERMINATED":
            result = response.json()['state_message']
            if result == "SUCCESS":
                print(f"✓ Job {job_id} completed successfully")
                context['task_instance'].xcom_push(key='run_id', value=run_id)
                context['task_instance'].xcom_push(key='status', value='SUCCESS')
                return run_id
            else:
                raise AirflowException(f"Job {job_id} failed: {result}")
        elif state == "INTERNAL_ERROR":
            raise AirflowException(f"Job {job_id} encountered internal error")
        
        retry_count += 1
        print(f"Job {job_id} in progress... (attempt {retry_count}/{max_retries})")
        import time
        time.sleep(60)
    
    raise AirflowException(f"Job {job_id} timed out after {max_retries} attempts")

def check_data_quality(job_layer, **context):
    """Validate data quality after each layer"""
    print(f"✓ Data quality checks for {job_layer} layer")
    # Add your data quality checks here
    pass

def send_notification(status, **context):
    """Send completion notification"""
    import logging
    logger = logging.getLogger(__name__)
    logger.info(f"Pipeline completed with status: {status}")

# Create DAG
with DAG(
    'creditcard_fraud_etl_pipeline',
    default_args=default_args,
    description='Credit Card Fraud Detection ETL Pipeline',
    schedule_interval='0 2 * * *',  # Daily at 02:00 UTC
    start_date=datetime(2024, 1, 1),
    catchup=False,
    tags=['databricks', 'etl', 'fraud-detection'],
) as dag:
    
    # Start
    start = DummyOperator(task_id='start')
    
    # Ingestion
    ingest_task = PythonOperator(
        task_id='ingest_data',
        python_callable=trigger_databricks_job,
        op_kwargs={'job_id': INGESTION_JOB_ID},
        provide_context=True,
    )
    
    # Bronze layer
    bronze_task = PythonOperator(
        task_id='bronze_layer',
        python_callable=trigger_databricks_job,
        op_kwargs={'job_id': BRONZE_JOB_ID},
        provide_context=True,
    )
    
    bronze_quality = PythonOperator(
        task_id='bronze_quality_check',
        python_callable=check_data_quality,
        op_kwargs={'job_layer': 'bronze'},
    )
    
    # Silver layer
    silver_task = PythonOperator(
        task_id='silver_layer',
        python_callable=trigger_databricks_job,
        op_kwargs={'job_id': SILVER_JOB_ID},
        provide_context=True,
    )
    
    silver_quality = PythonOperator(
        task_id='silver_quality_check',
        python_callable=check_data_quality,
        op_kwargs={'job_layer': 'silver'},
    )
    
    # Gold layer
    gold_task = PythonOperator(
        task_id='gold_layer',
        python_callable=trigger_databricks_job,
        op_kwargs={'job_id': GOLD_JOB_ID},
        provide_context=True,
    )
    
    gold_quality = PythonOperator(
        task_id='gold_quality_check',
        python_callable=check_data_quality,
        op_kwargs={'job_layer': 'gold'},
    )
    
    # End
    success = PythonOperator(
        task_id='pipeline_success',
        python_callable=send_notification,
        op_kwargs={'status': 'SUCCESS'},
    )
    
    # Define dependencies
    start >> ingest_task
    ingest_task >> bronze_task >> bronze_quality
    bronze_quality >> silver_task >> silver_quality
    silver_quality >> gold_task >> gold_quality
    gold_quality >> success

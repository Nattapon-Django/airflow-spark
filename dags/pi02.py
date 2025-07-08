from airflow import DAG
from airflow.providers.apache.spark.operators.spark_submit import SparkSubmitOperator
from datetime import datetime

# Define default_args
default_args = {
    'owner': 'airflow',
    'start_date': datetime(2025, 3, 18),
    'retries': 1,
}

# Define the DAG
dag = DAG(
    'spark_job_dag',
    default_args=default_args,
    description='A simple Spark job DAG',
    schedule_interval=None,  # Change to your desired schedule interval
)

# Define the SparkSubmitOperator
spark_submit_task = SparkSubmitOperator(
    task_id='spark_submit_task',
    conn_id='spark_default',  # Assuming you have a Spark connection setup
    application='/usr/local/spark/app/your_spark_script.py',  # Path to your Spark job
    name='airflow-spark-job',
    verbose=True,
    executor_memory='2g',
    total_executor_cores=2,
    driver_memory='1g',
    conf={'spark.driver.extraJavaOptions': '-Dlog4j.configuration=log4j.properties'},
    dag=dag
)

# Set the task in the DAG
spark_submit_task

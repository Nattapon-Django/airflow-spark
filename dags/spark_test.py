from airflow.providers.apache.spark.operators.spark_submit import SparkSubmitOperator

import datetime
import pendulum
import os

import requests
from airflow.decorators import dag, task

@dag(
    dag_id="spark-test",
    schedule_interval="0 0 * * *",
    start_date=pendulum.datetime(2021, 1, 1, tz="UTC"),
    catchup=False,
    dagrun_timeout=datetime.timedelta(minutes=60),
)
def SparkTest():
    create_task = SparkSubmitOperator(
        application='/opt/airflow/dags/pi.py',
        conn_id='spark_default',
        task_id='find-digits-of-pi'
    )

    create_task

dag = SparkTest()
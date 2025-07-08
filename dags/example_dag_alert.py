# example_dag.py

from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.utils.dates import days_ago
from datetime import timedelta
from msteams_alert import msteams_task_failure_alert  # import callback ที่เราแยกไว้

with DAG(
    dag_id='example_with_teams_alert',
    start_date=days_ago(1),
    schedule_interval=timedelta(days=1),
    catchup=False,
    tags=['example'],
    on_failure_callback=msteams_task_failure_alert,  # ใช้งาน callback ได้เลย
) as dag:
    def _failing_task():
        raise RuntimeError("This will fail!")

    task_fail = PythonOperator(
        task_id='fail_task',
        python_callable=_failing_task,
    )   
    task_fail  # ใช้งาน task นี้ใน DAG
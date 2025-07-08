import requests
import json
from airflow.models.dag import DAG
from airflow.operators.python import PythonOperator
from airflow.utils.dates import days_ago
from datetime import timedelta
from dotenv import load_dotenv
import os
load_dotenv()
# --- 1. กำหนด URL ของ MS Teams Webhook ---
# เปลี่ยนเป็น URL ที่คุณคัดลอกมาจากขั้นตอนการสร้าง Webhook ใน Teams
MS_TEAMS_WEBHOOK_URL = os.getenv("MS_TEAMS_WEBHOOK_URL")

# --- 2. สร้างฟังก์ชันสำหรับส่งข้อความไปยัง MS Teams ---
def send_msteams_message(message_text, message_color="FF0000"): # Default to red for errors
    """
    Sends a message to Microsoft Teams via an Incoming Webhook.
    
    Args:
        message_text (str): The main text content of the message.
        message_color (str): Hex color code for the message card (e.g., "FF0000" for red).
    """
    if not MS_TEAMS_WEBHOOK_URL:
        print("MS_TEAMS_WEBHOOK_URL is not set. Cannot send Teams message.")
        return

    # Teams uses a specific JSON format for messages (MessageCard)
    # Learn more: https://learn.microsoft.com/en-us/microsoftteams/platform/webhooks-and-connectors/how-to-create-and-send-messages?tabs=json%2Cjavascript
    payload = {
        "@type": "MessageCard",
        "@context": "http://schema.org/extensions",
        "themeColor": message_color,
        "summary": "Airflow Alert",
        "sections": [
            {
                "activityTitle": "Airflow Notification",
                "activitySubtitle": "A pipeline event occurred",
                "text": message_text
            }
        ]
    }

    try:
        response = requests.post(
            MS_TEAMS_WEBHOOK_URL,
            headers={"Content-Type": "application/json"},
            data=json.dumps(payload)
        )
        response.raise_for_status() # Raises an HTTPError for bad responses (4xx or 5xx)
        print("Message successfully sent to Microsoft Teams.")
    except requests.exceptions.RequestException as e:
        print(f"Failed to send message to Microsoft Teams: {e}")

# --- 3. สร้าง Callback Function สำหรับ Airflow (เช่น เมื่อ Task ล้มเหลว) ---
def msteams_task_failure_alert(context):
    dag_id = context['dag'].dag_id
    task_id = context['task_instance'].task_id
    logical_date = context['logical_date'].isoformat() # Convert to string for better display
    exception = context.get('exception') # Get exception if available
    log_url = context['task_instance'].log_url
    
    message = (
        f"🚨 **Airflow Task Failed!** 🚨\n"
        f"**DAG:** `{dag_id}`\n"
        f"**Task:** `{task_id}`\n"
        f"**Logical Date:** `{logical_date}`\n"
        f"**Error:** `{str(exception)[:500] if exception else 'N/A'}`\n" # Limit error message length
        f"[View Logs]({log_url})" # Link to Airflow UI logs
    )
    
    send_msteams_message(message, message_color="FF0000") # Red color for failure

# --- 4. สร้าง DAG และนำ Callback ไปใช้ ---
with DAG(
    dag_id='msteams_alerting_example',
    start_date=days_ago(1),
    schedule_interval=timedelta(days=1),
    catchup=False,
    tags=['msteams', 'alerting'],
    # กำหนด callback ที่ระดับ DAG
    on_failure_callback=msteams_task_failure_alert,
) as dag:
    def _succeeding_task():
        print("This task succeeds!")

    def _failing_task():
        # This task will fail, triggering the alert
        raise ValueError("Simulating a task failure for Teams alert!")

    task_succeed = PythonOperator(
        task_id='succeeding_task',
        python_callable=_succeeding_task,
    )

    task_fail = PythonOperator(
        task_id='failing_task',
        python_callable=_failing_task,
        # สามารถกำหนด callback ที่ระดับ Task ได้ด้วย (จะ override ระดับ DAG ถ้ามี)
        # on_failure_callback=msteams_task_failure_alert,
    )

    task_succeed >> task_fail
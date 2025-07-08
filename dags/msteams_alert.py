# msteams_alert.py

import requests
import json

from dotenv import load_dotenv
import os
load_dotenv()
# --- 1. กำหนด URL ของ MS Teams Webhook ---
# เปลี่ยนเป็น URL ที่คุณคัดลอกมาจากขั้นตอนการสร้าง Webhook ใน Teams
MS_TEAMS_WEBHOOK_URL = os.getenv("MS_TEAMS_WEBHOOK_URL")
# --- 2. สร้างฟังก์ชันสำหรับส่งข้อความไปยัง MS Teams ---
def send_msteams_message(message_text, message_color="FF0000"):
    """
    ส่งข้อความไปยัง MS Teams ผ่าน Webhook
    """
    if not MS_TEAMS_WEBHOOK_URL:
        print("MS_TEAMS_WEBHOOK_URL is not set.")
        return

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
        response.raise_for_status()
        print("Message sent to MS Teams.")
    except requests.exceptions.RequestException as e:
        print(f"Failed to send message to MS Teams: {e}")

def msteams_task_failure_alert(context):
    """
    Callback ใช้เมื่อ task fail ใน Airflow
    """
    dag_id = context['dag'].dag_id
    task_id = context['task_instance'].task_id
    logical_date = context['logical_date'].isoformat()
    exception = context.get('exception')
    log_url = context['task_instance'].log_url

    message = (
        f"🚨 **Airflow Task Failed!** 🚨\n"
        f"**DAG:** `{dag_id}`\n"
        f"**Task:** `{task_id}`\n"
        f"**Logical Date:** `{logical_date}`\n"
        f"**Error:** `{str(exception)[:500] if exception else 'N/A'}`\n"
        f"[View Logs]({log_url})"
    )

    send_msteams_message(message, message_color="FF0000")
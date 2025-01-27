from typing import List
import time
# import smtplib

from celery import Celery
from pydantic import EmailStr

# Initialize Celery app
celery_app = Celery('tasks', broker='redis://localhost:6379/0')

# Update configuration
celery_app.conf.update(
    task_routes={
        'src.celery_app.send_email_task': {'queue': 'email_queue'},
    },
    imports=["celery_app"]
)

@celery_app.task
def send_email_task(subject: str, recipients: List[EmailStr], body: str):
    print(f"Sending '{subject}' to: {', '.join(recipients)}...")

    # NOTE: Sleeping to simulate the email being sent.
    # Here I would use a synchronous email library like smtplib to actually send the email
    # but I don't have an email server configured to actually do that.
    time.sleep(1)

    print(f"Email sent!")

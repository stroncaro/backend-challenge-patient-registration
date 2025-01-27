from typing import List
import time
# import smtplib

from pydantic import EmailStr

from background_tasks import celery_app

@celery_app.task
def send_email_task(subject: str, recipients: List[EmailStr], body: str):
    """Celery task for sending emails. Use send_email instead."""
    print(f"Sending '{subject}' to: {', '.join(recipients)}...")

    # NOTE: Sleeping to simulate the email being sent.
    # Here I would use a synchronous email library like smtplib to actually send the email
    # but I don't have an email server configured to actually do that. Would have loved to
    # try doing that but I ran out of time.
    time.sleep(1)

    print(f"Email sent!")

# Wrapper to abstract away celery task implementation
def send_email(subject: str, recipients: List[EmailStr], body: str):
    """Send email in the background."""
    send_email_task.delay(subject, recipients, body) # type: ignore

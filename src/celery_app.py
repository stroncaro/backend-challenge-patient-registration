import time

from celery import Celery

# Initialize Celery app
celery_app = Celery('tasks', broker='redis://localhost:6379/0')

# Update configuration
celery_app.conf.update(
    task_routes={
        'src.celery_app.send_email_task': {'queue': 'email_queue'},  # Fully qualified name
    },
    imports=["celery_app"]  # Ensure Celery knows where to find the task
)

@celery_app.task
def send_email_task():
    print("!!! starting task")
    time.sleep(1)
    print("!!! finishing task")

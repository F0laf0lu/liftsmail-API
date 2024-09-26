from time import sleep
from celery import shared_task
from celery.utils.log import get_task_logger

from emailsending.utils import send_email

logger = get_task_logger(__name__)


@shared_task
def send_email_task(subject, message, recipient):
    print(f"Sending email to {recipient} with subject: {subject}")
    send_email(subject, message, recipient)

@shared_task
def add(x, y):
    return x + y


@shared_task
def sample_task():
    logger.info("The sample task just ran")
    return '----------liftsmail celery beat test complete---------'


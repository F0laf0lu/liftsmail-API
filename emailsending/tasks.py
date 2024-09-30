from time import sleep
from celery import shared_task
from celery.utils.log import get_task_logger
from django.core.mail import send_mass_mail
from emailsending.utils import format_email, send_email
from django.core.mail import send_mail

logger = get_task_logger(__name__)


@shared_task
def send_email_task(subject, message, recipient):
    print(f"Sending email to {recipient} with subject: {subject}")
    send_email(subject, message, recipient)


@shared_task
def send_bulk_emails(subject, html_message, sender_email, contact_list):
    """
    Sends emails to each contact in the contact list.
    """
    for contact in contact_list:
        # Personalize the message for each contact
        personalized_message = format_email(html_message, {
            "first_name": contact['first_name'],
            "last_name": contact['last_name'],
            "email": contact['email'],
            "contact_id": contact['id'],
        })

        # Send the email
        send_mail(
            subject=subject,
            message=None,  # Optional plain-text message
            from_email=sender_email,
            recipient_list=[contact['email']],  # Send to the specific contact
            fail_silently=False,
            html_message=personalized_message  # Send HTML message
        )


@shared_task
def add(x, y):
    return x + y


@shared_task
def sample_task():
    logger.info("The sample task just ran")
    return '----------liftsmail celery beat test complete---------'
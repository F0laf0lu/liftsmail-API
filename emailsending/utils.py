import os
import zoneinfo
from django.core.mail import EmailMessage
from django.template.loader import render_to_string
import tempfile
import random
import string


def generate_html_file_name(identifier):
    """
    Generates a unique filename based on the given identifier and a random 15-character alphanumeric string.
    
    Args:
        identifier (str): The identifier to use in the filename.
    
    Returns:
        str: The generated filename with a random 15-character string.
    """
    # Generate a random 15-character alphanumeric string
    random_string = ''.join(random.choices(string.ascii_letters + string.digits, k=15))
    
    # Combine the identifier and random string to create the filename
    return f"emailtemplate_{identifier}_{random_string}.html"
        

def format_email(message, context):
    """
    Renders the email template content with the given context.
    
    Args:
        message (str): The email message content.
        context (dict): The context data to render the template.
    
    Returns:
        str: The rendered email content.
    """
    # Generate a unique filename
    contact_id = context.get('contact_id')
    filename = generate_html_file_name(contact_id)
    
    # Create a temporary file
    temp_file_path = os.path.join('templates', filename)
    
    try:
        # Write the message content to the temporary file
        with open(temp_file_path, 'w') as file:
            file.write(message)
        
        # Render the template with context
        rendered_content = render_to_string(filename, context)
    
    finally:
        # Remove the temporary file
        if os.path.exists(temp_file_path):
            os.remove(temp_file_path)
    return rendered_content


def send_email(subject, message, recipient):
    """
    Sends an email using the given subject, message content, and recipient email.
    
    Args:
        subject (str): The subject of the email.
        message (str): The HTML content of the email.
        recipient (str): The recipient's email address.
    """
    email = EmailMessage(
        subject=subject,
        body=message,
        to=[recipient],
    )
    email.content_subtype = "html"
    email.send()


def format_messages(subject, message, contact_list, sender_email):
    """
    Sends multiple emails to different contacts using Django's send_mass_mail.
    """
    messages = []
    for contact in contact_list:
        personalized_message = format_email(message, {
            "first_name": contact['first_name'],
            "last_name": contact['last_name'],
            "email": contact['email'],
            "contact_id": contact['id'],
        })
        
        # Prepare the email tuple: (subject, message, from_email, [recipient_email])
        email_tuple = (
            subject,
            personalized_message,
            sender_email,  # Sender's email address
            [contact['email']]  # List of recipients (in this case, one recipient)
        )
        messages.append(email_tuple)

    return messages


    # send_mass_mail(messages, fail_silently=False)

from django.core.mail import send_mail

def send_html_emails(subject, html_message, contact_list, sender_email):
    """
    Sends multiple emails with HTML content to different contacts using send_mail.
    """
    for contact in contact_list:
        personalized_message = format_email(html_message, {
            "first_name": contact['first_name'],
            "last_name": contact['last_name'],
            "email": contact['email'],
            "contact_id": contact['id'],
        })
        
        # Send the email with HTML content
        send_mail(
            subject=subject,
            message=None,  # Plain text version (optional, leave as None if not required)
            from_email=sender_email,  # Sender email address
            recipient_list=[contact['email']],  # Recipient's email
            fail_silently=False,
            html_message=personalized_message  # Send HTML message
        )

import os
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
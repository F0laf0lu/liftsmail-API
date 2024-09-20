from django.contrib.auth.models import User
from rest_framework.test import APITestCase
from rest_framework import status
from emailsending.models import EmailTemplate, EmailSession
from emailcontacts.models import Group, Contact
from django.urls import reverse

class BaseTestCase(APITestCase):
    def setUp(self):
        # Create a user
        self.user = User.objects.create_user(username='testuser', password='password123')

        # Create a group and contacts
        self.group = Group.objects.create(name="Test Group", user=self.user)
        self.contact1 = Contact.objects.create(first_name="John", last_name="Doe", email="john@example.com", group=self.group)
        self.contact2 = Contact.objects.create(first_name="Jane", last_name="Doe", email="jane@example.com", group=self.group)

        # Create an email template
        self.template = EmailTemplate.objects.create(
            user=self.user,
            subject="Test Subject",
            body="Hello {{ first_name }} {{ last_name }}, this is a test email."
        )

        # API URLs
        self.templates_url = reverse('email-template-detail', kwargs={"pk": self.template.pk})
        self.send_email_url = reverse('send-mail')
        self.sessions_url = reverse('email-sessions')

        # Authentication
        self.client.authenticate(self.user)


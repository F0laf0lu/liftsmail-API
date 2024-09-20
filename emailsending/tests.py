from django.contrib.auth import get_user_model
from rest_framework.test import APITestCase
from rest_framework import status
from emailsending.models import EmailTemplate, EmailSession
from emailcontacts.models import Group, Contact
from django.urls import reverse

User = get_user_model()

class BaseTestCase(APITestCase):
    def setUp(self):
        # Create a user
        self.user = User.objects.create_user(email='testuser@app.com', password='password123')

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
        self.templates_url = reverse('email-templates')
        self.templates_detail_url = reverse('email-template-detail', kwargs={"pk": self.template.pk})
        self.send_email_url = reverse('send-mail')
        self.sessions_url = reverse('email-sessions')

        # Authentication
        self.client.force_authenticate(self.user)


class EmailTemplateTests(BaseTestCase):

    def test_list_email_templates(self):
        response = self.client.get(self.templates_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('Test Subject', str(response.data))

    def test_create_email_template(self):
        data = {
            "name":"New Template",
            "subject": "New Subject",
            "body": "New Body"
        }
        response = self.client.post(self.templates_url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['subject'], "New Subject")

    def test_update_email_template(self):
        data = {
            "subject": "Updated Subject",
            "body": "Updated Body"
        }
        response = self.client.patch(self.templates_detail_url, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['subject'], "Updated Subject")

    def test_delete_email_template(self):
        response = self.client.delete(self.templates_detail_url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(EmailTemplate.objects.filter(pk=self.template.pk).exists())

class SendEmailTests(BaseTestCase):

    def test_send_email(self):
        data = {
            "template": {
                "subject": self.template.subject,
                "body": self.template.body
            },
            "group_id": self.group.pk
        }
        response = self.client.post(self.send_email_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("Emails sent successfully", response.data['message'])

    def test_send_email_to_empty_group(self):
        # Create an empty group with no contacts
        empty_group = Group.objects.create(name="Empty Group", user=self.user)
        data = {
            "template": {
                "subject": self.template.subject,
                "body": self.template.body
            },
            "group_id": empty_group.pk
        }
        response = self.client.post(self.send_email_url, data,  format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("This group has no contacts", response.data['detail'])

class EmailSessionTests(BaseTestCase):
    def test_list_email_sessions(self):
        # Create a dummy email session
        EmailSession.objects.create(user=self.user, session="Session Test", group_id=self.group, template_id=self.template)
        
        response = self.client.get(self.sessions_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('Session Test', str(response.data))


class PermissionTests(BaseTestCase):
    def test_unauthorized_access(self):
        self.client.logout()
        response = self.client.get(self.templates_url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_access_other_users_templates(self):
        other_user = User.objects.create_user(email='otheruser@app.com', password='password123')
        other_template = EmailTemplate.objects.create(
            user=other_user, subject="Other Subject", body="Other Body"
        )
        url = reverse('email-template-detail', kwargs={"pk": other_template.pk})
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

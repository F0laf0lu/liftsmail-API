import os
from django.urls import reverse
from django.contrib.auth import get_user_model
from rest_framework import status
from rest_framework.test import APITestCase
from emailcontacts.models import Group, Contact

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'liftsmail.settings')

User = get_user_model()


class GroupViewTest(APITestCase):
    def setUp(self):
        self.user = User.objects.create(email='testuser@app.com', password="password")
        self.group = Group.objects.create(name="Test Group", user=self.user)
        self.contact_data = {
            "first_name": "John",
            "last_name": "Doe",
            "email": "john.doe@example.com",
        }

    def test_create_group(self):
        url = reverse('group-list-create')
        self.assertEqual('/api/v1/groups/', url)

        data = {
            'name':'New Group'
        }

        self.client.force_authenticate(self.user)
        response = self.client.post(url, data=data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Group.objects.count(), 2)

    def test_add_contact_to_group(self):
        url = reverse('contact-list-create', kwargs={'pk': self.group.id})
        self.client.force_authenticate(self.user)
        response = self.client.post(url, self.contact_data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Contact.objects.count(), 1)
        self.assertEqual(Contact.objects.get(id=response.data['id']).email, 'john.doe@example.com')

    def test_add_duplicate_contact_to_group(self):
        Contact.objects.create(group=self.group, **self.contact_data)
        url = reverse('contact-list-create', kwargs={'pk': self.group.id})
        self.client.force_authenticate(self.user)
        response = self.client.post(url, self.contact_data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_not_group_owner_add_contact_to_group(self):
        user = User.objects.create(email='user@app.com', password="password")
        url = reverse('contact-list-create', kwargs={'pk': self.group.id})
        self.client.force_authenticate(user)
        response = self.client.post(url, self.contact_data)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_get_group_contacts(self):
        Contact.objects.create(group=self.group, **self.contact_data)
        url = reverse('contact-list-create', kwargs={'pk': self.group.id})
        self.client.force_authenticate(self.user)
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['email'], 'john.doe@example.com')

    def test_delete_contact(self):
        contact = Contact.objects.create(group=self.group, **self.contact_data)
        url = reverse('contact-detail', kwargs={'group_id': self.group.id, 'pk': contact.id})
        self.client.force_authenticate(self.user)
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(Contact.objects.count(), 0)
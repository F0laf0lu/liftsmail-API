from django.db import IntegrityError
from django.test import TestCase
from django.contrib.auth import get_user_model
from ..models import CustomUser

class CustomUserManagerTests(TestCase):

    def test_create_user(self):
        User = get_user_model()
        user = User.objects.create_user(email='testuser@email.com', password='password123')

        self.assertEqual(user.email, 'testuser@email.com')
        self.assertFalse(user.is_staff)
        self.assertFalse(user.is_superuser)
        self.assertTrue(user.is_active)

    def test_create_superuser(self):
        User = get_user_model()
        admin_user = User.objects.create_superuser(email='adminuser@email.com', password='adminpassword')

        self.assertEqual(admin_user.email, 'adminuser@email.com')
        self.assertTrue(admin_user.is_staff)
        self.assertTrue(admin_user.is_superuser)
        self.assertTrue(admin_user.is_active)

    def test_create_user_missing_email(self):
        User = get_user_model()
        with self.assertRaises(ValueError):
            User.objects.create_user(email='', password='password123')

    def test_create_superuser_not_staff(self):
        User = get_user_model()
        with self.assertRaises(ValueError):
            User.objects.create_superuser(email='adminuser@email.com', password='superpassword', is_staff=False)

    def test_create_superuser_not_superuser(self):
        User = get_user_model()
        with self.assertRaises(ValueError):
            User.objects.create_superuser(email='adminuser@email.com', password='superpassword', is_superuser=False)

class CustomUserModelTests(TestCase):
    def test_user_str_method(self):
        user = CustomUser(email='testuser@email.com')
        self.assertEqual(str(user), 'testuser@email.com')

    def test_user_email_is_unique(self):
            user1 = CustomUser.objects.create_user(email='testuser@email.com', password='password123')

            with self.assertRaises(IntegrityError):
                user2 = CustomUser.objects.create_user(email='testuser@email.com', password='password123')
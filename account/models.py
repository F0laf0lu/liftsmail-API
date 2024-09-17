from django.db import models
from django.contrib.auth.models import AbstractUser
from account.managers import UserManager
# Create your models here.


class CustomUser(AbstractUser):
    username = None
    email = models.EmailField("email address", unique=True)
    is_verified = models.BooleanField(default=False)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []
    
    objects = UserManager()

    def __str__(self) -> str:
        return self.email
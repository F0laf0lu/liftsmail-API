from django.db import models
from django.contrib.auth import get_user_model
from liftsmail.models import TimeStampBaseModel


User = get_user_model()


class Group(TimeStampBaseModel):
    name = models.CharField(max_length=255, unique=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="emailgroups")

    def __str__(self):
        return f'{self.name} by <{self.user.email}>'
    
    class Meta:
        ordering = ['-created_at']

class Contact(TimeStampBaseModel):
    first_name = models.CharField(max_length=255,null=True)
    last_name = models.CharField(max_length=255, null=True)
    email = models.EmailField()
    is_subscribed = models.BooleanField(default=True)
    is_valid = models.BooleanField(default=True)
    group = models.ForeignKey(Group, related_name='contacts', on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.first_name} {self.last_name} <{self.email}>"
    
    class Meta:
        ordering = ['-created_at']

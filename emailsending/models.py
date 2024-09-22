from django.db import models
from django.contrib.auth import get_user_model
from liftsmail.models import TimeStampBaseModel
from emailcontacts.models import Group

User = get_user_model()


class EmailTemplate(TimeStampBaseModel):
    name = models.CharField(max_length=50)
    subject = models.CharField(max_length=50)
    body = models.TextField()
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    
    def __str__(self):
        return f"{self.name}-{self.user.id}"
    
    class Meta:
        unique_together = ['user',"name"]


class EmailSession(TimeStampBaseModel):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    session = models.CharField(max_length=255, blank=True, null=True)
    group_id = models.ForeignKey(Group, on_delete=models.CASCADE)
    template_id = models.ForeignKey(EmailTemplate, on_delete=models.CASCADE, null=True, blank=True)
    is_scheduled = models.BooleanField(default=False)
    schedule_time = models.DateTimeField(null=True, blank=True)
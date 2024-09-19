from django.contrib import admin
from .models import EmailSession, EmailTemplate

# Register your models here.

admin.site.register(EmailTemplate)
admin.site.register(EmailSession)
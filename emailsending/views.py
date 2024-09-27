from datetime import timedelta
import zoneinfo
from django.utils.timezone import make_aware
import json
from django.utils.timezone import now
from rest_framework import generics
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from emailcontacts.permissions import  IsGroupOwner, IsOwner
from django_celery_beat.models import CrontabSchedule, PeriodicTask, ClockedSchedule, IntervalSchedule
from emailsending.serializers import EmailSessionSerializer, EmailTemplatesSerializers, SendNowSerializer, ScheduleSerializer
from emailsending.tasks import send_email_task
from emailsending.utils import format_email, send_email
from .models import EmailSession, EmailTemplate

# Create your views here.
class EmailTemplatesListCreateApiView(generics.ListCreateAPIView):
    queryset = EmailTemplate.objects.all()
    serializer_class = EmailTemplatesSerializers
    permission_classes = [IsAuthenticated, IsGroupOwner]

    def get_queryset(self):
        return  EmailTemplate.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)
        return super().perform_create(serializer)

class EmailTemplateDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = EmailTemplate.objects.all()
    serializer_class = EmailTemplatesSerializers
    permission_classes = [IsAuthenticated,IsOwner]

    # def get_queryset(self):        
    #     return EmailTemplate.objects.filter(user=self.request.user.id)

class EmailSessionView(generics.ListAPIView):
    queryset  = EmailSession.objects.all()
    serializer_class = EmailSessionSerializer
    permission_classes = [IsAuthenticated, IsGroupOwner]

    def get_queryset(self):
        return EmailSession.objects.filter(user=self.request.user)

class SendMailView(generics.CreateAPIView):
    serializer_class = SendNowSerializer
    permission_classes = [IsAuthenticated]
    queryset = EmailSession.objects.all()

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        template = serializer.validated_data['template']
        group = serializer.validated_data['group_id']

        message = template["body"]
        subject = template["subject"]

        contacts = group.contacts.all()

        if not contacts:
            return Response({"detail": "This group has no contacts"}, status=400)
        
        for contact in contacts:
            context = {
                "first_name": contact.first_name if contact.first_name else "Guest",
                'last_name': contact.last_name if contact.last_name else "Guest",
                'email': contact.email,
                "contact_id": contact.id
            }
            new_message = format_email(message, context)
            send_email_task.delay(message=new_message, subject=subject, recipient=contact.email)
        serializer.save()
        return Response({"message": "Emails sent successfully"})

class ScheduleEmailView(generics.CreateAPIView):
    serializer_class = ScheduleSerializer
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        schedule_time = serializer.validated_data['schedule_time']
        group = serializer.validated_data['group_id']
        template = serializer.validated_data['template_id']
        message = template.body
        subject = template.subject
        contacts = group.contacts.all()
        for contact in contacts:
            context = {
                "first_name": contact.first_name if contact.first_name else "Guest",
                'last_name': contact.last_name if contact.last_name else "Guest",
                'email': contact.email,
                "contact_id": contact.id
            }
            new_message = format_email(message, context)
            schedule, _ = CrontabSchedule.objects.get_or_create(
                        minute=schedule_time.minute,
                        hour=schedule_time.hour,
                        day_of_month=schedule_time.day,
                        month_of_year=schedule_time.month,
                        day_of_week=schedule_time.strftime('%w'),
                        timezone=zoneinfo.ZoneInfo('Africa/Lagos')
                        )
            PeriodicTask.objects.create(
                crontab = schedule,
                name = f'mail_{contact.id}_{now().timestamp()}',
                task = 'emailsending.tasks.send_email_task',
                args = json.dumps([new_message, subject, contact.email]),
                one_off = True,
            )
        return Response({"message": "Emails scheduled successfully"})

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)
        return super().perform_create(serializer)


'''
Schedule Email sending

Description: To schedule the sending of an email at a later time
That is, create a email session at a later time other than now

- Create email session serializer with all fields including, is_scheduled and schedule_time
- pick template from already created user template
- pick the schedule time
- create celery task 
- send the task to celery
- when celery executes the task create email session.
'''


# Ways to provide context to serializer
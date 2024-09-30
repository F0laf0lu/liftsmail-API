from datetime import timezone
import zoneinfo
import json
from django.utils.timezone import now
from rest_framework import generics, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from emailcontacts.permissions import  IsGroupOwner, IsOwner
from django_celery_beat.models import CrontabSchedule, PeriodicTask, IntervalSchedule
from emailsending.serializers import EmailSessionSerializer, EmailTemplatesSerializers, SendNowSerializer, ScheduleSerializer, RecurringEmailSerilaizer
from emailsending.tasks import send_email_task
from emailsending.utils import format_email, send_email, format_messages
from .models import EmailSession, EmailTemplate
from django.core.mail import send_mass_mail


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
        return self.create(request, *args, **kwargs)

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

        schedule, _ = CrontabSchedule.objects.get_or_create(
            minute=schedule_time.minute,
            hour=schedule_time.hour,
            day_of_month=schedule_time.day,
            month_of_year=schedule_time.month,
            day_of_week=schedule_time.strftime('%w'),
            timezone=zoneinfo.ZoneInfo('Africa/Lagos')
            )
        cleaned_body = template.body.replace('\n', '').replace('<br>', '<br>').replace('\r', '<br>')
        contact_list = [
            {
                "first_name": contact.first_name or "Guest",
                'last_name': contact.last_name or "Guest",
                'email': contact.email,
                "id": contact.id
            }
            for contact in group.contacts.all()
        ]
        sender_email=request.user.email

        try:
            PeriodicTask.objects.create(
                crontab=schedule,
                name=f'mail_{group.id}_{now().timestamp()}',
                task='emailsending.tasks.send_bulk_emails',
                args=json.dumps([subject, cleaned_body, sender_email, contact_list]),
                one_off=True,
            )
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        return self.create(request, *args, **kwargs)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)
        return super().perform_create(serializer)

class RecurringEmailView(generics.CreateAPIView):
    serializer_class = RecurringEmailSerilaizer
    queryset = EmailSession.objects.all()
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        validated_data = serializer.validated_data

        group = validated_data.get('group_id')
        template = validated_data.get('template_id')
        interval = validated_data.get('interval')
        repeats_every = validated_data.get('repeats_every')
        time = validated_data.get('time')
        starts = validated_data.get('starts')
        ends = validated_data.get('ends')
        cleaned_body = template.body.replace('\n', '').replace('<br>', '<br>').replace('\r', '<br>')

        schedule, _ = self.get_crontab_schedule(repeats_every, time, interval, starts)

        contact_list = [
            {
                "first_name": contact.first_name or "Guest",
                'last_name': contact.last_name or "Guest",
                'email': contact.email,
                "id": contact.id
            }
            for contact in group.contacts.all()
        ]
        sender_email=request.user.email

        try:
            PeriodicTask.objects.create(
                crontab=schedule,
                name=f'mail_{group.id}_{now().timestamp()}',
                task='emailsending.tasks.send_bulk_emails',
                args=json.dumps([template.subject, cleaned_body, sender_email, contact_list]),
                start_time=starts,
                expires=ends,
                one_off=False,
            )
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        return self.create(request, *args, **kwargs)
    
    def get_serializer_context(self):
        context = super().get_serializer_context()
        context['user'] = self.request.user
        return context

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)
        return super().perform_create(serializer)

    def get_crontab_schedule(self, repeats_every, time, interval, starts):
        if repeats_every == 'day':
            return CrontabSchedule.objects.get_or_create(
                minute=time.minute, hour=time.hour,
                day_of_month=f'*/{interval}', month_of_year='*',
                day_of_week='*', timezone=zoneinfo.ZoneInfo('Africa/Lagos')
            )
        elif repeats_every == 'week':
            return CrontabSchedule.objects.get_or_create(
                minute=time.minute, hour=time.hour,
                day_of_month='*', month_of_year='*',
                day_of_week=starts.strftime('%w'), timezone=zoneinfo.ZoneInfo('Africa/Lagos')
            )
        elif repeats_every == 'month':
            return CrontabSchedule.objects.get_or_create(
                minute=time.minute, hour=time.hour,
                day_of_month=starts.day, month_of_year=f'*/{interval}',
                day_of_week='*', timezone=zoneinfo.ZoneInfo('Africa/Lagos')
            )
        elif repeats_every == 'year':
            return CrontabSchedule.objects.get_or_create(
                minute=time.minute, hour=time.hour,
                day_of_month=starts.day, month_of_year=starts.month,
                day_of_week='*', timezone=zoneinfo.ZoneInfo('Africa/Lagos')
            )

# Schedules supported for now
# Every X days
# Every x weeks - once per week
# Every x month - once per month
# Every 1 year 


# Todo
# 5 email sessions per user
# 50 emails per user
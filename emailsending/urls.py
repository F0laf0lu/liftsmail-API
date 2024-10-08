from .views import EmailSessionView, EmailTemplateDetailView, EmailTemplatesListCreateApiView, SendMailView, ScheduleEmailView, RecurringEmailView
from django.urls import path


urlpatterns = [
    path('templates/', EmailTemplatesListCreateApiView.as_view(), name='email-templates'),
    path('templates/<int:pk>/', EmailTemplateDetailView.as_view(), name='email-template-detail'),
    path('send/', SendMailView.as_view(), name='send-mail'),
    path('schedule/', ScheduleEmailView.as_view(), name='schedule-email' ),
    path('schedule/recurring', RecurringEmailView.as_view(), name='recuring-email' ),
    path('sessions/', EmailSessionView.as_view(), name="email-sessions"),
]

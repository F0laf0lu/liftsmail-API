from .views import EmailSessionView, EmailTemplateDetailView, EmailTemplatesListCreateApiView, SendMailView
from django.urls import path


urlpatterns = [
    path('templates/', EmailTemplatesListCreateApiView.as_view()),
    path('templates/<int:pk>/', EmailTemplateDetailView.as_view(), name='email-template-detail'),
    path('send/', SendMailView.as_view(), name='send-mail'),
    path('sessions/', EmailSessionView.as_view(), name="email-sessions"),
]

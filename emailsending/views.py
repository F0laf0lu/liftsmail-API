from rest_framework import generics
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from rest_framework.response import Response
from emailcontacts.permissions import  IsGroupOwner, IsOwner
from emailsending.serializers import EmailSessionSerializer, EmailTemplatesSerializers, SendNowSerializer
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
            send_email(message=new_message, subject=subject, recipient=contact.email)
            print(serializer.validated_data)
            serializer.save()
        return Response({"message": "Emails sent successfully"})


class EmailSessionView(generics.ListAPIView):
    queryset  = EmailSession.objects.all()
    serializer_class = EmailSessionSerializer
    permission_classes = [IsAuthenticated, IsGroupOwner]

    def get_queryset(self):
        return EmailSession.objects.filter(user=self.request.user)
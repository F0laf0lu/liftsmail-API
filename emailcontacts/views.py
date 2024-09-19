from django.shortcuts import get_object_or_404
from rest_framework import generics, status, serializers
from rest_framework.permissions import IsAuthenticated
from emailcontacts.serializers import ContactSerializer, GroupSerializer
from .models import Group, Contact
from .permissions import IsGroupOwner
# Create your views here.

# List or create groups
class GroupListCreateView(generics.ListCreateAPIView):
    queryset = Group.objects.all()
    serializer_class = GroupSerializer
    permission_classes = [IsAuthenticated]

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    def get_queryset(self):
        context =  super().get_queryset()
        return context.filter(user=self.request.user)

# Group details
class GroupDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Group.objects.all()
    serializer_class = GroupSerializer
    permission_classes = [IsAuthenticated, IsGroupOwner]

# Create contacts within a group, list all contacts in a group
class ContactListCreateView(generics.ListCreateAPIView):
    serializer_class = ContactSerializer
    permission_classes = [IsAuthenticated, IsGroupOwner]

    def get_group(self):
        if getattr(self, 'swagger_fake_view', False):
            return None
        
        group_id = self.kwargs['pk']
        group = get_object_or_404(Group, id=group_id)
        self.check_object_permissions(self.request, group)
        return group
    
    def get_queryset(self):
        group = self.get_group()
        return Contact.objects.filter(group=group)

    def perform_create(self, serializer):
        group = self.get_group()
        email = serializer.validated_data['email']
    
        existing_contact = Contact.objects.filter(email=email, group=group).first()
        if existing_contact:
            raise serializers.ValidationError({'email': ['Contact with this email already exists in the group.']})
        serializer.save(group=group)


# view a contact detail
class ContactDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Contact.objects.all()
    serializer_class = ContactSerializer
    permission_classes = [IsAuthenticated, IsGroupOwner]
    
    def get_object(self):
        # Short-circuit for schema generation
        if getattr(self, 'swagger_fake_view', False):
            return None
        
        group_id = self.kwargs.get('group_id')
        contact_id = self.kwargs.get('pk')
        
        if not group_id or not contact_id:
            raise KeyError("Missing 'group_id' or 'pk' in the URL kwargs")

        group = get_object_or_404(Group, id=group_id)
        self.check_object_permissions(self.request, group)
        
        contact = get_object_or_404(Contact, id=contact_id, group=group)
        return contact

# todo
# - Process email lists from csv, json
# -	add emails to the email group through a list of objects, or processed files.
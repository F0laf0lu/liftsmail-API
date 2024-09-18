from rest_framework import serializers
from .models import Group, Contact


class ContactSerializer(serializers.ModelSerializer):
    class Meta:
        model = Contact
        fields = '__all__'
        read_only_fields = ('group','is_subscribed','is_valid')
        
    def validate_email(self,value):
        value = value.lower().strip()
        return value


class GroupSerializer(serializers.ModelSerializer):
    contacts = ContactSerializer(many=True, read_only=True)

    class Meta:
        model = Group
        fields = '__all__'
        read_only_fields = ('user',)
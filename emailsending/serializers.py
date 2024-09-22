from emailcontacts.models import Group
from .models import EmailTemplate, EmailSession
from rest_framework import serializers


class EmailTemplatesSerializers(serializers.ModelSerializer):
    class Meta:
        model = EmailTemplate
        exclude = ['user']

class SimpleEmailTemplatesSerializers(serializers.ModelSerializer):
    class Meta:
        model = EmailTemplate
        exclude = ['user', 'name']

class SendNowSerializer(serializers.ModelSerializer):
    template = SimpleEmailTemplatesSerializers() 
    class Meta:
        model = EmailSession
        fields = ['id', 'user', 'session', 'group_id', 'template']
        read_only_fields = ('user',)

    def __init__(self, *args, **kwargs):
        super(SendNowSerializer, self).__init__(*args, **kwargs)
        request = self.context.get('request', None)

        if request and hasattr(request, 'user') and request.user.is_authenticated:
            user = request.user
            self.fields['group_id'].queryset = Group.objects.filter(user=user)

    def create(self, validated_data):
        session = validated_data.get('session', None)
        group_id = validated_data['group_id']
        user = self.context.get('request').user
        EmailSession.objects.create(session=session, group_id=group_id, user=user)
        return EmailSession


class EmailSessionSerializer(serializers.ModelSerializer):
    class Meta:
        model = EmailSession
        fields = '__all__'
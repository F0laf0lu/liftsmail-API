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

    # To list only users group in the group_id drop down
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

class ScheduleSerializer(serializers.ModelSerializer):
    class Meta:
        model = EmailSession
        exclude = ['user', 'one_off']

    def __init__(self, **kwargs):
        super(ScheduleSerializer, self).__init__(**kwargs)
        request = self.context.get('request',  None)
        if request and hasattr(request, 'user') and request.user.is_authenticated:
            user = request.user
            self.fields['template_id'].queryset = EmailTemplate.objects.filter(user=user)
            self.fields['group_id'].queryset = Group.objects.filter(user=user)

    def validate(self, attrs):
        session = attrs.get('session', None)
        template_id = attrs.get('template_id', None)
        schedule_time = attrs.get('schedule_time', None)
        if not session:
            raise serializers.ValidationError("Session is required")
        if not template_id:
            raise serializers.ValidationError('Template is required')
        if not schedule_time:
            raise serializers.ValidationError('You need to set schedule time')
        return super().validate(attrs)

    def validate_group_id(self, value):
        contacts = value.contacts.all()
        if len(contacts) == 0:
            raise serializers.ValidationError("Group has no contacts")
        return value


class RecurringEmailSerilaizer(serializers.ModelSerializer):
    REPEAT_CHOICES = [
        ('day', 'Day'),
        ('week', 'Week'),
        ('month','Month'),
        ('year', 'Year')
    ]
    interval = serializers.IntegerField(required=False, min_value=1)
    repeats_every = serializers.ChoiceField(required=True, choices=REPEAT_CHOICES)
    time = serializers.TimeField(required=True)
    starts = serializers.DateField(required=True)
    ends = serializers.DateField(required=False)

    class Meta:
        model = EmailSession
        fields = ['session', 'group_id', 'template_id',  'interval', 'repeats_every', 'time', 'starts', 'ends']

    def __init__(self, **kwargs):
        super(RecurringEmailSerilaizer, self).__init__(**kwargs)
        request = self.context.get('request',  None)
        if request and hasattr(request, 'user') and request.user.is_authenticated:
            user = request.user
            self.fields['template_id'].queryset = EmailTemplate.objects.filter(user=user)
            self.fields['group_id'].queryset = Group.objects.filter(user=user)


    def validate(self, data):
        starts = data.get('starts') 
        ends = data.get('ends')
        session = data.get('session', None)
        template_id = data.get('template_id', None)

        if not session:
            raise serializers.ValidationError("Session is required")
        if not template_id:
            raise serializers.ValidationError('Template is required')
        if starts and ends and ends <= starts:
            raise serializers.ValidationError("End date must be after the start date.")
        return data

    def validate_group_id(self, value):
        contacts = value.contacts.all()
        if len(contacts) == 0:
            raise serializers.ValidationError("Group has no contacts")
        return value
    
    def create(self, validated_data):
        print(self.context)
        Emailsession = EmailSession.objects.create(
            user = self.context.get('user'),
            session = validated_data['session'],
            group_id = validated_data['group_id'],
            template_id = validated_data['template_id']
        )
        return Emailsession

class EmailSessionSerializer(serializers.ModelSerializer):
    class Meta:
        model = EmailSession
        fields = '__all__'



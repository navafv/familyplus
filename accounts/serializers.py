from rest_framework import serializers
from .models import Account, UserProfile, ContactMessage, NewsletterSubscriber
from django.contrib.auth.password_validation import validate_password

class UserProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserProfile
        fields = ['address_line_1', 'address_line_2', 'city', 'state', 'country', 'profile_picture']

class UserSerializer(serializers.ModelSerializer):
    # The source is 'userprofile' because the OneToOneField relates to Account
    profile = UserProfileSerializer(source='userprofile')

    class Meta:
        model = Account
        fields = ['first_name', 'last_name', 'email', 'phone_number', 'profile']
        read_only_fields = ['email'] # Email usually shouldn't be changed without re-verification

    def update(self, instance, validated_data):
        # Extract the nested profile data
        profile_data = validated_data.pop('userprofile', None)
        
        # Update the Account fields
        instance.first_name = validated_data.get('first_name', instance.first_name)
        instance.last_name = validated_data.get('last_name', instance.last_name)
        instance.phone_number = validated_data.get('phone_number', instance.phone_number)
        instance.save()

        # Update the nested UserProfile fields
        if profile_data:
            profile = instance.userprofile
            profile.address_line_1 = profile_data.get('address_line_1', profile.address_line_1)
            profile.address_line_2 = profile_data.get('address_line_2', profile.address_line_2)
            profile.city = profile_data.get('city', profile.city)
            profile.state = profile_data.get('state', profile.state)
            profile.country = profile_data.get('country', profile.country)
            
            if 'profile_picture' in profile_data:
                profile.profile_picture = profile_data.get('profile_picture')
            profile.save()

        return instance

class RegistrationSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, required=True, validators=[validate_password])
    confirm_password = serializers.CharField(write_only=True, required=True)

    class Meta:
        model = Account
        fields = ['first_name', 'last_name', 'phone_number', 'email', 'password', 'confirm_password']

    def validate(self, attrs):
        if attrs['password'] != attrs['confirm_password']:
            raise serializers.ValidationError({"password": "Password fields didn't match."})
        return attrs

    def create(self, validated_data):
        email = validated_data['email']
        username = email.split('@')[0]
        
        user = Account.objects.create_user(
            first_name=validated_data['first_name'],
            last_name=validated_data['last_name'],
            email=email,
            username=username,
            password=validated_data['password']
        )
        user.phone_number = validated_data.get('phone_number', '')
        user.is_active = False  # Must verify email first
        user.save()

        # Automatically create the linked UserProfile with a default picture
        UserProfile.objects.create(user=user, profile_picture='default/default-user.png')
        
        return user

class ChangePasswordSerializer(serializers.Serializer):
    current_password = serializers.CharField(required=True)
    new_password = serializers.CharField(required=True, validators=[validate_password])
    confirm_password = serializers.CharField(required=True)

    def validate(self, attrs):
        if attrs['new_password'] != attrs['confirm_password']:
            raise serializers.ValidationError({"new_password": "New passwords didn't match."})
        return attrs

class ContactMessageSerializer(serializers.ModelSerializer):
    class Meta:
        model = ContactMessage
        fields = '__all__'

class NewsletterSubscriberSerializer(serializers.ModelSerializer):
    class Meta:
        model = NewsletterSubscriber
        fields = '__all__'

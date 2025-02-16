from rest_framework import serializers
from .models import Help, Lesion, HelpLesion, CustomUser

class HelpSerializer(serializers.ModelSerializer):
    class Meta:
        model = Help
        fields = '__all__'
        read_only_fields = ['image_url']

class HelpLesionSerializer(serializers.ModelSerializer):
    class Meta:
        model = HelpLesion
        fields = ['help', 'quantity']

class LesionSerializer(serializers.ModelSerializer):
    help_lesions = HelpLesionSerializer(many=True, read_only=True)
    
    class Meta:
        model = Lesion
        fields = '__all__'
        read_only_fields = ['creator', 'moderator', 'created_at', 'formed_at', 'completed_at']

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = ('id', 'username', 'email', 'password', 'is_moderator')
        extra_kwargs = {'password': {'write_only': True}}

class LoginSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField()

    def validate(self, data):
        user = CustomUser.objects.filter(email=data['email']).first()
        if user and user.check_password(data['password']):
            return user
        raise serializers.ValidationError("Invalid credentials")
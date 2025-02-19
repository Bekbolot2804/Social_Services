from rest_framework import serializers
from .models import Help, Lesion, HelpLesion

class HelpSerializer(serializers.ModelSerializer):
    class Meta:
        model = Help
        fields = '__all__'
        read_only_fields = ['image_url']

class HelpLesionSerializer(serializers.ModelSerializer):
    help = HelpSerializer(read_only=True)
    class Meta:
        model = HelpLesion
        fields = ['help', 'quantity']

class LesionSerializer(serializers.ModelSerializer):
    help_lesions = HelpLesionSerializer(many=True, read_only=True)
    
    class Meta:
        model = Lesion
        fields = '__all__'
        read_only_fields = ['creator', 'moderator', 'created_at', 'formed_at', 'completed_at']
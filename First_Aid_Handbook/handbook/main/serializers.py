from rest_framework import serializers
from .models import Help, Lesion, HelpLesion  # Импорт всех моделей

class HelpSerializer(serializers.ModelSerializer):
    class Meta:
        model = Help
        fields = '__all__'

class LesionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Lesion
        fields = '__all__'
        read_only_fields = ['id', 'date_start', 'date_end']

class HelpLesionSerializer(serializers.ModelSerializer):
    help = HelpSerializer(read_only=True)
    lesion = LesionSerializer(read_only=True)

    class Meta:
        model = HelpLesion
        fields = '__all__'
        read_only_fields = ['id']
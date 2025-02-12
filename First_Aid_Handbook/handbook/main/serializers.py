# main/serializer.py

from rest_framework import serializers
from .models import Help

class HelpSerializer(serializers.ModelSerializer):
    pic = serializers.ImageField(write_only=True, required=False)  # Временное поле для загрузки файла
    image = serializers.CharField(read_only=True)  # Поле только для чтения (URL)

    class Meta:
        model = Help
        fields = ['id', 'name', 'title', 'description', 'image', 'pic', 'duration']

    def create(self, validated_data):
        # Удаляем поле 'pic' из validated_data, так как оно не является частью модели
        validated_data.pop('pic', None)
        return super().create(validated_data)
# main/serializer.py

from rest_framework import serializers
from .models import Help, Lesion, HelpLesion, CustomUser

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

class LesionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Lesion
        fields = ['id', 'name', 'status', 'creator', 'moderator', 'created_at', 
                 'date_formed', 'date_completed', 'disaster_type']
        read_only_fields = ['creator', 'moderator', 'created_at', 'date_formed', 'date_completed']
class LesionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Lesion
        fields = ['id', 'name', 'status', 'creator', 'moderator', 'created_at', 'date_formed', 'date_completed', 'disaster_type']
        read_only_fields = ['creator', 'moderator', 'created_at', 'date_formed', 'date_completed']
class HelpLesionSerializer(serializers.ModelSerializer):
    class Meta:
        model = HelpLesion
        fields = ['help', 'lesion', 'application_order', 'notes']
        read_only_fields = ['lesion']
class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = ['id', 'username', 'email', 'first_name', 'last_name']

class HelpLesionDetailSerializer(serializers.ModelSerializer):
    help = HelpSerializer(read_only=True)
    
    class Meta:
        model = HelpLesion
        fields = ['help', 'quantity', 'application_order', 'notes']

class LesionDetailSerializer(LesionSerializer):
    help_lesions = HelpLesionDetailSerializer(many=True, read_only=True)
    creator = UserSerializer(read_only=True)
    
    class Meta(LesionSerializer.Meta):
        fields = LesionSerializer.Meta.fields + ['help_lesions', 'total_cost']
from .models import *
from rest_framework import serializers
from collections import OrderedDict

class AttributeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Attribute
        fields = '__all__'
        read_only_fields = ['attribute_id']

class AttributeHelpSerializer(serializers.ModelSerializer):
    attribute = AttributeSerializer(read_only=True)

    class Meta:
        model = Attribute_help
        fields = ['attribute', 'value']
        read_only_fields =['attribute']

class HelpForAttributesSerializer(serializers.ModelSerializer):
    attributes = AttributeHelpSerializer(many=True, read_only=True, source='help_attributes')

    class Meta:
        model = Help
        fields = ['attributes']
        read_only_fields = ['attributes']

class CustomUserSerializer(serializers.ModelSerializer):
    is_staff = serializers.BooleanField(default=False, required=False)
    is_superuser = serializers.BooleanField(default=False, required=False)
    class Meta:
        model = CustomUser
        fields = ['email', 'password', 'is_staff', 'is_superuser']

        def get_fields(self):
            new_fields = OrderedDict()
            for name, field in super().get_fields().items():
                field.required = False
                new_fields[name] = field
            return new_fields 

class SwaggerCustomUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = ['email', 'password']

        def get_fields(self):
            new_fields = OrderedDict()
            for name, field in super().get_fields().items():
                field.required = False
                new_fields[name] = field
            return new_fields 

class HelpSerializer(serializers.ModelSerializer):
    class Meta:
        model = Help
        fields = '__all__'
        read_only_fields = ['help_id']
        

    def get_fields(self):
        new_fields = OrderedDict()
        for name, field in super().get_fields().items():
            if name == 'img_url':
                field.required = False
            else:
                field.required = True
            new_fields[name] = field
        return new_fields 

class HelpForLesionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Help
        fields = ['help_id', 'name', 'status', 'img_url']
        read_only_fields = ['help_id', 'status']

        def get_fields(self):
            new_fields = OrderedDict()
            for name, field in super().get_fields().items():
                field.required = False
                new_fields[name] = field
            return new_fields 

class HelpLesionSerializer(serializers.ModelSerializer):
    help = HelpForLesionSerializer(read_only=True)

    class Meta:
        model = Help_lesion
        fields = '__all__'
        read_only_fields = ['id', 'lesion', 'help', 'remaining_quantity']

        def get_fields(self):
            new_fields = OrderedDict()
            for name, field in super().get_fields().items():
                field.required = False
                new_fields[name] = field
            return new_fields 

class LesionSerializer(serializers.ModelSerializer):
    helps = HelpLesionSerializer(many=True, read_only=True, source='lesion_helps')
    creator = serializers.StringRelatedField()
    moderator = serializers.StringRelatedField()

    class Meta:
        model = Lesion
        fields = '__all__'
        read_only_fields = ['lesion_id', 'creator', 'moderator', 'status', 'date_of_creation', 'date_of_formation', 'date_of_finish', 'qr']

        def get_fields(self):
            new_fields = OrderedDict()
            for name, field in super().get_fields().items():
                field.required = False
                new_fields[name] = field
            return new_fields 
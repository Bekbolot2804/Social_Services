from main.models import Help
from main.models import Lesion
from main.models import HelpLesion
from main.models import AuthUser
from rest_framework import serializers



class HelpSerializer(serializers.ModelSerializer):
    class Meta:
        model = Help
        fields = ["pk", "name", "title", "description", "url", "user"]

class UserSerializer(serializers.ModelSerializer):
    stock_set = HelpSerializer(many=True, read_only=True)

    class Meta:
        model = AuthUser
        fields = ["id", "first_name", "last_name", "stock_set"]

class LesionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Lesion
        fields = ["pk", "name", "status", "date_start", "date_end", "date_applied", "creator", "moderator"]

class HelpLesionSerializer(serializers.ModelSerializer):
    lesion = LesionSerializer(read_only=True)
    help = HelpSerializer(read_only=True)
    class Meta:
        model = HelpLesion
        fields = ["pk", "help", "lesion", "time", "comment"]
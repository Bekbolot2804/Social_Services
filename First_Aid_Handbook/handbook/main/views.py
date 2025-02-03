from rest_framework.response import Response
from rest_framework.views import APIView
from django.forms.models import model_to_dict
from .models import Help
from .serializers import HelpSerializer

class HelpAPIview(APIView):
    def get(self, request):
        lst=Help.objects.all().values()
        return Response(list(lst)) 
    def post(self, request):
        post_new = Help.objects.create(
            name=request.data['name'],
            image=request.data['image'],
            title=request.data['title'],
            description=request.data['description'],
        )
        return Response('post:', model_to_dict(post_new))
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.decorators import api_view
from rest_framework import status
from django.shortcuts import get_object_or_404
from django.forms.models import model_to_dict
from .models import Help
from .serializers import HelpSerializer
from .minio import add_pic



class HelpList(APIView):
    model_class = Help
    serializer_class = HelpSerializer
    def get(self, request):
        helps=self.model_class.objects.all()
        serializer=self.serializer_class(helps, many=True)
        return Response(serializer.data)
    def post(self, request, format=None):
        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid():
            help = serializer.save()
            pic = request.FILES.get("pic")
            pic_result = add_pic(help, pic)
            if 'error' in pic_result.data:
                return Response({"errors": "Че ошибка?"})
                # return pic_result
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    # def post(self, request):
    #     serializer=self.serializer_class(data=request.data)
    #     if serializer.is_valid():
    #         serializer.save()
    #         return Response(serializer.data, status=status.HTTP_201_CREATED)
    #     return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
class HelpDetail(APIView):
    model_class = Help
    serializer_class = HelpSerializer
    def get(self, request, pk):
        help=get_object_or_404(self.model_class, pk=pk)
        serializer=self.serializer_class(help)
        return Response(serializer.data)
    def put(self, request, pk):
        help=get_object_or_404(self.model_class, pk=pk)
        serializer=self.serializer_class(help, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    def delete(self, request, pk):
        help=get_object_or_404(self.model_class, pk=pk)
        help.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
# Обновляет информацию об акции (для пользователя) 
@api_view(['PUT'])
def put(self, request, pk):
    help=get_object_or_404(Help, pk=pk)
    serializer=self.serializer_class(help, data=request.data, partial=True)
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
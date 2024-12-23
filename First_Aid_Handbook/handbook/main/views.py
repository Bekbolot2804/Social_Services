from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from django.shortcuts import get_object_or_404
from rest_framework import status 
from main.serializers import HelpSerializer
from main.serializers import LesionSerializer
from main.serializers import HelpLesionSerializer
from main.serializers import UserSerializer
from main.models import Help
from main.models import Lesion
from main.models import HelpLesion
from main.models import AuthUser
from main.minio import add_pic
from rest_framework.views import APIView
from rest_framework.decorators import api_view


def user():
    try:
        user1 = AuthUser.objects.get(id=1)
    except:
        user1 = AuthUser(id=1, first_name='John', last_name='Doe', password=1234, username="user1")
        user1.save()
    return user1

class HelpList(APIView):
    model_class = Help
    serializer_class = HelpSerializer

    def get(self, request, format=None):
        stocks = self.model_class.objects.all()

        # Применение фильтров вручную
        filter_backends = [DjangoFilterBackend()]
        for backend in filter_backends:
            stocks = backend.filter_queryset(request, stocks, view=self)

        
        serializer = self.serializer_class(stocks, many=True)
        return Response(serializer.data)
    def post(self, request, fomat=None):
        serializer = self.serializer_class(data = request.data)
        if serializer.is_valid():
            stock=serializer.save()
            pic=request.FILES.get("pic")
            pic_result=add_pic(stock, pic)
            if 'error' in pic_result.data:
                return pic_result
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class HelpDetail(APIView):
    model_class = Help
    serializer_class = HelpSerializer

    def get(self, request, pk, format=None):
        stock = get_object_or_404(self.model_class, pk=pk)
        serializer = self.serializer_class(stock)
        return Response(serializer.data)
    def put(self, request, pk, format=None):
        stock = get_object_or_404(self.model_class, pk=pk)
        serializer = self.serializer_class(stock, data=request.data, partial=True)
        if 'pic' in serializer.initial_data:
            pic_result = add_pic(stock, serializer.initial_data['pic'])
            if 'error' in pic_result.data:
                return pic_result
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    def delete(self, request, pk, format=None):
        stock = get_object_or_404(self.model_class, pk=pk)
        stock.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
    
@api_view(['Put'])
def put(self, request, pk, format=None):
    stock = get_object_or_404(Help, pk=pk)
    serializer = HelpSerializer(stock, data=request.data, partial=True)
    if 'pic' in serializer.initial_data:
        pic_result = add_pic(stock, serializer.initial_data['pic'])
        if 'error' in pic_result.data:
            return pic_result
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class UsersList(APIView):
    model_class = AuthUser
    serializer_class = UserSerializer

    def get(self, request, format=None):
        user = self.model_class.objects.all()
        serializer = self.serializer_class(user, many=True)
        return Response(serializer.data)
    
class LesionList(APIView):
    model_class = Lesion
    settings_class = LesionSerializer
    def get(self, request, format=None):
        stocks = self.model_class.objects.all()
        serializer = self.settings_class(stocks, many=True)
        return Response(serializer.data)

class LesionDetail(APIView):
    model_class = Lesion
    settings_class = LesionSerializer
    def get(self, request, pk, format=None):
        stock = get_object_or_404(self.model_class, pk=pk)
        serializer = self.settings_class(stock)
        return Response(serializer.data)
    def put(self, request, pk, format=None):
        stock = get_object_or_404(self.model_class, pk=pk)
        serializer = self.serializer_class(stock, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    def delete(self, request, pk, format=None):
        stock = get_object_or_404(self.model_class, pk=pk)
        stock.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
    
class LesionHelpsEdit(APIView):
    model_class = HelpLesion
    settings_class = HelpLesionSerializer
    
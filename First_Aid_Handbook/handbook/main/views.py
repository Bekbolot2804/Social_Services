from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.db import IntegrityError
from django.shortcuts import get_object_or_404
from django.contrib.auth import authenticate
from main.minio import add_pic
from .models import Help, Lesion, HelpLesion
from .serializers import HelpSerializer, LesionSerializer, HelpLesionSerializer

class HelpView(APIView):
    def get(self, request, id=None):
        if id:
            instance = get_object_or_404(Help, id=id)
            serializer = HelpSerializer(instance)
        else:
            helps = Help.objects.all()
            serializer = HelpSerializer(helps, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def post(self, request):
        serializer = HelpSerializer(data=request.data)
        if serializer.is_valid():
            try:
                # Сохраняем объект Help
                help_instance = serializer.save()

                # Обрабатываем загруженное изображение
                pic = request.FILES.get("pic")
                if pic:
                    pic_result = add_pic(help_instance, pic)  # Передаем правильный объект Help
                    if 'error' in pic_result:
                        return Response(pic_result, status=status.HTTP_400_BAD_REQUEST)
                
                return Response(serializer.data, status=status.HTTP_201_CREATED)
            except IntegrityError as e:
                return Response({"error": "Integrity Error: Duplicate or invalid data"}, status=status.HTTP_400_BAD_REQUEST)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def put(self, request, id):
        instance = get_object_or_404(Help, id=id)
        serializer = HelpSerializer(instance, data=request.data, partial=True)
        if 'pic' in serializer.initial_data:
            pic_result = add_pic(help, serializer.initial_data['pic'])
            if 'error' in pic_result.data:
                return pic_result
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, id):
        instance = get_object_or_404(Help, id=id)
        instance.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class LesionView(APIView):
    def get(self, request, id=None):
        if id:
            instance = get_object_or_404(Lesion, id=id)
            serializer = LesionSerializer(instance)
        else:
            lesions = Lesion.objects.all()
            serializer = LesionSerializer(lesions, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def post(self, request):
        serializer = LesionSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def put(self, request, id):
        instance = get_object_or_404(Lesion, id=id)
        serializer = LesionSerializer(instance, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, id):
        instance = get_object_or_404(Lesion, id=id)
        instance.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class LesionStatusUpdateView(APIView):
    def put(self, request, id):
        lesion = get_object_or_404(Lesion, id=id)
        new_status = request.data.get('status')
        if new_status:
            lesion.status = new_status
            lesion.save()
            return Response({"message": "Status updated successfully"}, status=status.HTTP_200_OK)
        return Response({"error": "Status not provided"}, status=status.HTTP_400_BAD_REQUEST)


class HelpLesionView(APIView):
    def get(self, request, id=None):
        if id:
            instance = get_object_or_404(HelpLesion, id=id)
            serializer = HelpLesionSerializer(instance)
        else:
            help_lesions = HelpLesion.objects.all()
            serializer = HelpLesionSerializer(help_lesions, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def post(self, request):
        serializer = HelpLesionSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def put(self, request, id):
        instance = get_object_or_404(HelpLesion, id=id)
        serializer = HelpLesionSerializer(instance, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, id):
        instance = get_object_or_404(HelpLesion, id=id)
        instance.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class UserLoginView(APIView):
    def post(self, request):
        username = request.data.get('username')
        password = request.data.get('password')
        user = authenticate(username=username, password=password)
        if user:
            return Response({"message": "Login successful"}, status=status.HTTP_200_OK)
        return Response({"error": "Invalid credentials"}, status=status.HTTP_401_UNAUTHORIZED)


class UserLogoutView(APIView):
    def post(self, request):
        return Response({"message": "Logout successful"}, status=status.HTTP_200_OK)


class HelpLesionTimeUpdateView(APIView):
    def put(self, request, id):
        help_lesion = get_object_or_404(HelpLesion, id=id)
        new_time = request.data.get('time')
        if new_time:
            help_lesion.time = new_time
            help_lesion.save()
            return Response({"message": "Time updated successfully"}, status=status.HTTP_200_OK)
        return Response({"error": "Time not provided"}, status=status.HTTP_400_BAD_REQUEST)

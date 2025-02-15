from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.decorators import permission_classes  # Добавьте этот импорт
from django.shortcuts import get_object_or_404
from drf_spectacular.utils import extend_schema, OpenApiResponse
from django.utils import timezone
from .models import Help, Lesion, HelpLesion, CustomUser
from .serializers import HelpSerializer, LesionSerializer, HelpLesionSerializer
from .minio import upload_image
from .serializers import UserSerializer, LoginSerializer
from .permissions import IsModerator, IsCreator  # Добавьте этот импорт
import uuid
import redis

session_storage = redis.StrictRedis(host='localhost', port=6379)

class UserRegistration(APIView):
    def post(self, request):
        serializer = UserSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            return Response({'user_id': user.id}, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class LoginView(APIView):
    def post(self, request):
        serializer = LoginSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.validated_data
            session_id = str(uuid.uuid4())
            session_storage.set(session_id, user.email)
            response = Response({'status': 'ok'})
            response.set_cookie('session_id', session_id)
            return response
        return Response({'error': 'Invalid credentials'}, status=401)

class LogoutView(APIView):
    def post(self, request):
        session_id = request.COOKIES.get('session_id')
        if session_id:
            session_storage.delete(session_id)
        response = Response({'status': 'logged out'})
        response.delete_cookie('session_id')
        return response

class HelpView(APIView):
    @extend_schema(
        summary="Get list of help types",
        responses={
            200: HelpSerializer(many=True),
            403: OpenApiResponse(description="Forbidden")
        }
    )
    def get(self, request):
        helps = Help.objects.filter(is_active=True)
        serializer = HelpSerializer(helps, many=True)
        return Response(serializer.data)

    def post(self, request):
        serializer = HelpSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class HelpDetailView(APIView):
    def get(self, request, pk):
        help = get_object_or_404(Help, pk=pk)
        serializer = HelpSerializer(help)
        return Response(serializer.data)

    def put(self, request, pk):
        help = get_object_or_404(Help, pk=pk)
        serializer = HelpSerializer(help, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk):
        help = get_object_or_404(Help, pk=pk)
        help.is_active = False
        help.save()
        return Response(status=status.HTTP_204_NO_CONTENT)

class LesionView(APIView):
    @permission_classes([IsModerator | IsCreator])  # Применяем декоратор к методу
    def get(self, request):
        if request.user.is_moderator:
            lesions = Lesion.objects.all()
        else:
            lesions = Lesion.objects.filter(creator=request.user)
        serializer = LesionSerializer(lesions, many=True)
        return Response(serializer.data)

class LesionDetailView(APIView):
    def get(self, request, pk):
        lesion = get_object_or_404(Lesion, pk=pk)
        serializer = LesionSerializer(lesion)
        return Response(serializer.data)

    @permission_classes([IsCreator])  # Применяем декоратор к методу
    def put(self, request, pk):
        lesion = self.get_object(pk)
        serializer = LesionSerializer(lesion, data=request.data, partial=True)
        
        if serializer.is_valid():
            new_status = request.data.get('status')
            if new_status and not self.validate_status(lesion.status, new_status):
                return Response({"error": "Invalid status transition"}, status=400)
            
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=400)

    def validate_status(self, old_status, new_status):
        transitions = {
            'draft': ['formed', 'deleted'],
            'formed': ['completed', 'rejected'],
            'completed': [],
            'rejected': [],
            'deleted': []
        }
        return new_status in transitions.get(old_status, [])

class LesionDraftView(APIView):
    def get(self, request):
        user = fixed_user()
        draft = Lesion.objects.filter(creator=user, status='draft').first()
        if not draft:
            draft = Lesion.objects.create(creator=user, status='draft')
        serializer = LesionSerializer(draft)
        return Response(serializer.data)

class HelpLesionView(APIView):
    def post(self, request, lesion_id):
        lesion = get_object_or_404(Lesion, pk=lesion_id)
        serializer = HelpLesionSerializer(data=request.data)
        
        if serializer.is_valid():
            if lesion.status != 'draft':
                return Response({"error": "Can only add to draft lesions"}, status=400)
            
            serializer.save(lesion=lesion)
            return Response(serializer.data, status=201)
        return Response(serializer.errors, status=400)

    def delete(self, request, lesion_id, help_id):
        relation = get_object_or_404(HelpLesion, lesion_id=lesion_id, help_id=help_id)
        relation.delete()
        return Response(status=204)

class ImageUploadView(APIView):
    def post(self, request, pk):
        help = get_object_or_404(Help, pk=pk)
        image = request.FILES.get('image')
        
        if not image:
            return Response({"error": "No image provided"}, status=400)
        
        url = upload_image(help, image)
        help.image_url = url
        help.save()
        
        return Response({"image_url": url}, status=200)
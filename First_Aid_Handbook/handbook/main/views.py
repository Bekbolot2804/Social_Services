from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.shortcuts import get_object_or_404
from django.utils import timezone
from .models import Help, Lesion, HelpLesion, CustomUser
from .serializers import HelpSerializer, LesionSerializer, HelpLesionSerializer, UserSerializer
from .minio import upload_image
from django.contrib.auth import authenticate, login, logout
from django.http import HttpResponse
from rest_framework.permissions import AllowAny
from django.views.decorators.csrf import csrf_exempt
from rest_framework.decorators import permission_classes
from rest_framework.decorators import permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.decorators import authentication_classes, permission_classes
from drf_yasg.utils import swagger_auto_schema
from rest_framework.decorators import api_view
from rest_framework import viewsets
from rest_framework.authentication import SessionAuthentication, BasicAuthentication
from rest_framework.decorators import authentication_classes
from rest_framework.permissions import IsAuthenticatedOrReadOnly
from rest_framework.permissions import IsAdminUser
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from django.conf import settings
import redis

# Connect to our Redis instance
session_storage = redis.StrictRedis(host=settings.REDIS_HOST, port=settings.REDIS_PORT)

@permission_classes([AllowAny])
@authentication_classes([])
@csrf_exempt
@swagger_auto_schema(method='post', request_body=UserSerializer)
@api_view(['Post'])
def login_view(request):
    username = request.POST["email"] 
    password = request.POST["password"]
    user = authenticate(request, email=username, password=password)
    if user is not None:
        random_key = uuid.uuid4()
        session_storage.set(random_key, username)

        response = HttpResponse("{'status': 'ok'}")
        response.set_cookie("session_id", random_key)

        return response
    else:
        return HttpResponse("{'status': 'error', 'error': 'login failed'}")
@authentication_classes([])
def logout_view(request):
    logout(request._request)
    return Response({'status': 'Success'})
class UserViewSet(viewsets.ModelViewSet):
    authentication_classes = [SessionAuthentication, BasicAuthentication]
    """Класс, описывающий методы работы с пользователями
    Осуществляет связь с таблицей пользователей в базе данных
    """
    queryset = CustomUser.objects.all()
    serializer_class = UserSerializer
    model_class = CustomUser
    def get_permissions(self):
        if self.action == 'create':
            permission_classes = [AllowAny]
        else:
            permission_classes = [IsAdminUser]
        return [permission() for permission in permission_classes]
    @method_decorator(csrf_exempt)
    def create(self, request):
        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid():
            # Используйте create_user вместо create!
            user = self.model_class.objects.create_user(
                email=serializer.validated_data['email'],
                password=serializer.validated_data['password'],
                is_staff=serializer.validated_data.get('is_staff', False),
                is_superuser=serializer.validated_data.get('is_superuser', False)
            )
            return Response({'status': 'Success'}, status=201)
        return Response(serializer.errors, status=400)
def method_permission_classes(classes):
    def decorator(func):
        def decorated_func(self, *args, **kwargs):
            self.permission_classes = classes        
            self.check_permissions(self.request)
            return func(self, *args, **kwargs)
        return decorated_func
    return decorator
def fixed_user():
    return CustomUser.objects.get_or_create(username='fixed_user')[0]

class HelpView(APIView):
    authentication_classes = [SessionAuthentication, BasicAuthentication]
    def get(self, request):
        helps = Help.objects.filter(is_active=True)
        serializer = HelpSerializer(helps, many=True)
        return Response(serializer.data)
    @swagger_auto_schema(request_body=HelpSerializer)
    def post(self, request):
        serializer = HelpSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class HelpDetailView(APIView):
    authentication_classes = [SessionAuthentication, BasicAuthentication]
    permission_classes = [IsAuthenticatedOrReadOnly]
    def get(self, request, pk):
        help = get_object_or_404(Help, pk=pk)
        serializer = HelpSerializer(help)
        return Response(serializer.data)
    @swagger_auto_schema(request_body=HelpSerializer)
    @method_permission_classes((IsAdminUser))
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
    def get(self, request):
        lesions = Lesion.objects.exclude(status__in=['deleted', 'draft'])
        serializer = LesionSerializer(lesions, many=True)
        return Response(serializer.data)

class LesionDetailView(APIView):
    def get(self, request, pk):
        lesion = get_object_or_404(Lesion, pk=pk)
        serializer = LesionSerializer(lesion)
        return Response(serializer.data)

    def put(self, request, pk):
        lesion = get_object_or_404(Lesion, pk=pk)
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
@swagger_auto_schema(method='put', request_body=HelpSerializer)
@api_view(['Put'])
@permission_classes([AllowAny])
@authentication_classes([])
def put_detail(request, pk, format=None):
    help = get_object_or_404(Help, pk=pk)
    serializer = HelpSerializer(help, data=request.data, partial=True)
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
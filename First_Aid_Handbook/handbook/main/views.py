from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.decorators import api_view
from rest_framework import status
from django.shortcuts import get_object_or_404
from django.forms.models import model_to_dict
from .models import Help, Lesion, HelpLesion
from .serializers import HelpSerializer, LesionSerializer, UserSerializer
from .minio import add_pic
from rest_framework.parsers import MultiPartParser
# main/views.py
from .models import Lesion  # Импорт модели Lesion
from django.contrib.auth import get_user_model
from rest_framework.permissions import IsAuthenticated

User = get_user_model()


class LesionCreateView(APIView):
    # permission_classes = [IsAuthenticated]  # Только аутентифицированные пользователи могут создавать заявки

    def post(self, request):
        fixed_user = User.objects.first()
        # Автоматически устанавливаем создателя заявки
        data = request.data.copy()
        data['creator'] = request.user.id if fixed_user else None
        data['status'] = 'draft'  # Статус по умолчанию

        serializer = LesionSerializer(data=data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
class HelpList(APIView):
    parser_classes = [MultiPartParser]
    model_class = Help
    serializer_class = HelpSerializer
    def get(self, request):
        helps=self.model_class.objects.all()
        serializer=self.serializer_class(helps, many=True)
        return Response(serializer.data)
    def post(self, request, format=None):
        # Создаем сериализатор с данными из запроса
        serializer = HelpSerializer(data=request.data)
        
        if serializer.is_valid():
            # Сохраняем объект без изображения
            help_instance = serializer.save()

            # Получаем файл из запроса
            pic = request.FILES.get("pic")
            if pic:
                # Загружаем изображение в MinIO и обновляем объект
                result = add_pic(help_instance, pic)
                if 'error' in result:
                    return Response({"errors": "Ошибка при загрузке изображения"}, status=status.HTTP_400_BAD_REQUEST)

            # Возвращаем обновленные данные
            response_serializer = HelpSerializer(help_instance)
            return Response(response_serializer.data, status=status.HTTP_201_CREATED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    
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

class LesionView(APIView):
    # permission_classes = [IsAuthenticated]
    def get(self, request):
        # Фильтрация по статусу и дате
        status_filter = request.query_params.get('status')
        start_date = request.query_params.get('start_date')
        end_date = request.query_params.get('end_date')
        
        queryset = Lesion.objects.exclude(status__in=['deleted', 'draft'])
        
        if status_filter:
            queryset = queryset.filter(status=status_filter)
        if start_date and end_date:
            queryset = queryset.filter(created_at__range=[start_date, end_date])
            
        serializer = LesionSerializer(queryset, many=True)
        return Response(serializer.data)
    def get_queryset(self):
        user = self.request.user
        if user.is_moderator:
            return Lesion.objects.exclude(status='deleted')
        return Lesion.objects.filter(creator=user).exclude(status='deleted')
    def put(self, request, pk=None):
        lesion = Lesion.objects.get(pk=pk)
        
        # Проверка изменения статуса
        new_status = request.data.get('status')
        if new_status and not self.validate_status_transition(lesion.status, new_status):
            return Response({"error": "Недопустимое изменение статуса"}, status=400)
        
        serializer = LesionSerializer(lesion, data=request.data, partial=True)
        if serializer.is_valid():
            updated_lesion = serializer.save()
            
            # Автоматическое заполнение полей при завершении
            if new_status == 'completed':
                updated_lesion.moderator = request.user
                updated_lesion.date_completed = timezone.now()
                updated_lesion.save()
            if new_status == 'completed':
                total = sum(h1.help.cost*h1.quantity for h1 in lesion.help_lesions.all())
                lesion.total_cost = total
                lesion.save()
            return Response(LesionSerializer(updated_lesion).data)
        return Response(serializer.errors, status=400)

    def validate_status_transition(self, old_status, new_status):
        allowed_transitions = {
            'draft': ['formed', 'deleted'],
            'formed': ['completed', 'rejected'],
            'completed': [],
            'rejected': [],
            'deleted': []
        }
        return new_status in allowed_transitions.get(old_status, [])

class HelpLesionView(APIView):
    def post(self, request, lesion_id):
        try:
            lesion = Lesion.objects.get(pk=lesion_id, status='draft')
            help_id = request.data.get('help_id')
            help_instance = Help.objects.get(pk=help_id)
            
            # Создание связи
            HelpLesion.objects.create(
                lesion=lesion,
                help=help_instance,
                application_order=request.data.get('application_order', 1),
                notes=request.data.get('notes', '')
            )
            
            return Response(status=status.HTTP_201_CREATED)
        except Lesion.DoesNotExist:
            return Response({"error": "Заявка не найдена или не в статусе черновика"}, status=404)
class UserRegisterView(APIView):
    def post(self, request):
        serializer = UserSerializer(data=request.data)
        if serializer.is_valid():
            user = User.objects.create_user(**serializer.validated_data)
            return Response(UserSerializer(user).data, status=201)
        return Response(serializer.errors, status=400)

class UserProfileView(APIView):
    def put(self, request, pk):
        user = get_object_or_404(User, pk=pk)
        serializer = UserSerializer(user, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=400)
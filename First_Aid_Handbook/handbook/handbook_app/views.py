from django.shortcuts import get_object_or_404
from django.utils.dateparse import parse_datetime
from django.utils import timezone
from django.contrib.auth import authenticate, logout
from django.views.decorators.csrf import csrf_exempt
from django.conf import settings
from django.db.models import Q

from .models import *
from .serializers import *
from .minio import deleteImg, addImg
from .permissions import IsManager, IsAdmin, AuthBySSID, IsAuth
from .redis import session_storage

from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes, authentication_classes
from rest_framework.permissions import AllowAny

from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi

import uuid

from .qr_generate import generate_lesion_qr

error_schema = openapi.Schema(
    type=openapi.TYPE_OBJECT,
    properties={
        'details': openapi.Schema(type=openapi.TYPE_STRING)
    },
    required=['details']
)

ok_schema = openapi.Schema(
    type=openapi.TYPE_OBJECT,
    properties={
        'status': openapi.Schema(type=openapi.TYPE_STRING)
    },
    required=['status']
)

def method_permission_classes(classes):
    def decorator(func):
        def decorated_func(self, *args, **kwargs):
            self.permission_classes = classes        
            self.check_permissions(self.request)
            return func(self, *args, **kwargs)
        return decorated_func
    return decorator

def getlesionInformation(user):
    lesion = user.user_lesions.all().filter(status='draft').first()
    if lesion is None:
        lesion_helps_count = 0 
        lesion_id = 0
    else:
        lesion_helps_count = Help_lesion.objects.filter(lesion_id=lesion.lesion_id).count()
        lesion_id = lesion.lesion_id

    return {'lesion_helps_count': lesion_helps_count, 
            'lesion_id': lesion_id}

@csrf_exempt
@swagger_auto_schema(method='post', 
                     request_body=SwaggerCustomUserSerializer,
                     responses={
                        200: openapi.Response(
                            description='Успешная аутентификация',
                            schema=CustomUserSerializer
                        ),
                        400: openapi.Response(
                            description='Ошибка входа',
                            schema=error_schema
                        )
})
@api_view(['post'])
@authentication_classes([AuthBySSID])
@permission_classes([AllowAny])
def login_view(request):
    username = request.data["email"] 
    password = request.data["password"]
    user = authenticate(request, email=username, password=password)
    if user is not None:
        random_key = str(uuid.uuid4())
        session_storage.set(random_key, username)

        response = Response(CustomUserSerializer(user).data, status=status.HTTP_200_OK)
        response.set_cookie("session_id", random_key)

        return response
    else:
        return Response({'details': 'login failed'}, status=status.HTTP_400_BAD_REQUEST)

@csrf_exempt
@swagger_auto_schema(method='post', 
                     request_body=None,
                     responses={
                        200: openapi.Response(
                            description='Успешный выход из системы',
                            schema=ok_schema
                        ),
                        400: openapi.Response(
                            description='Ошибка выхода из системы',
                            schema=error_schema
                        ),
                        403: openapi.Response(
                            description='Нет доступа',
                            schema=error_schema
                         )
})
@api_view(['post'])
@authentication_classes([AuthBySSID])
@permission_classes([IsAuth])
def logout_view(request):
    ssid = request.COOKIES.get("session_id")
    try:
        session_storage.delete(ssid)
        logout(request)
        return Response({'status': 'logged out'}, status=status.HTTP_200_OK)
    except Exception:
        return Response({'details': 'logout failed'}, status=status.HTTP_400_BAD_REQUEST)

class HelpsMethods(APIView):
    serializer = HelpSerializer
    authentication_classes = [AuthBySSID]

    @swagger_auto_schema(manual_parameters=[
                            openapi.Parameter(
                                name = 'name',
                                in_ = openapi.IN_QUERY,
                                description='Имя',
                                type=openapi.TYPE_STRING,
                                required=False
                            ),
                         ],
                         responses={
                            200: openapi.Response(
                                description='Протоколы первой помощи с номером черновой заявки и количеством в корзине',
                                schema=openapi.Schema(
                                    type=openapi.TYPE_OBJECT,
                                    properties={
                                        'name': openapi.Schema(type=openapi.TYPE_STRING),
                                        'helps': openapi.Schema(
                                            type=openapi.TYPE_ARRAY,
                                            items=openapi.Schema(type=openapi.TYPE_OBJECT,
                                                                 properties={
                                                                     'help_id': openapi.Schema(type=openapi.TYPE_INTEGER),
                                                                     'name': openapi.Schema(type=openapi.TYPE_STRING),
                                                                     'description': openapi.Schema(type=openapi.TYPE_STRING),
                                                                     'status': openapi.Schema(type=openapi.TYPE_STRING),
                                                                     'img_url': openapi.Schema(type=openapi.TYPE_STRING),
                                                                     'duration': openapi.Schema(type=openapi.TYPE_INTEGER)
                                                                 },
                                                                 required=['help_id', 
                                                                           'name', 
                                                                           'description', 
                                                                           'status', 
                                                                           'img_url', 
                                                                           'duration',
                                                                 ])
                                        ),
                                        'lesion_information': openapi.Schema(
                                            type=openapi.TYPE_OBJECT,
                                            properties={
                                                'lesion_helps_count': openapi.Schema(type=openapi.TYPE_INTEGER),
                                                'lesion_id': openapi.Schema(type=openapi.TYPE_INTEGER)
                                            },
                                            required=['lesion_helps_count', 'lesion_id']
                                        )
                                    },
                                    required=['name', 'helps', 'lesion_information']
                                )
                            )
    })
    @method_permission_classes([AllowAny])
    def get(self, request):
        search_name = request.query_params.get('name', '')
        helps = Help.objects.filter(name__icontains=search_name)
        if request.user.is_authenticated:
            lesion_information = getlesionInformation(request.user)
        else:
            lesion_information = {'lesion_helps_count': 0, 
                                 'lesion_id': 0}
        serial_data = self.serializer(helps, many = True)
        return Response({'name': search_name, 
                         'helps': serial_data.data, 
                         'lesion_information': lesion_information},
                         status=status.HTTP_200_OK)
    
    @swagger_auto_schema(request_body=serializer,
                         responses={
                            201: openapi.Response(
                                description='Успешное создание элемента',
                                schema=HelpSerializer
                            ),
                            403: openapi.Response(
                                description='Нет доступа',
                                schema=error_schema
                            )
    })
    @method_permission_classes([IsManager])
    def post(self, request):
        input_data = self.serializer(data=request.data)
        if input_data.is_valid():
            input_data.save()
            return Response(input_data.data, status=status.HTTP_201_CREATED)
        return Response(input_data.errors, status=status.HTTP_400_BAD_REQUEST)

class HelpMethods(APIView):
    serializer = HelpSerializer
    authentication_classes = [AuthBySSID]

    @swagger_auto_schema(responses={
                            200: openapi.Response(
                                description='Успешное получение одного протокола помощи',
                                schema=HelpSerializer
                            ),
                            404: openapi.Response(
                                description='Не нашли услугу с таким id',
                                schema=error_schema
                            )
    })
    @method_permission_classes([AllowAny])
    def get(self, request, help_id):
        help = get_object_or_404(Help, pk=help_id)
        if help.status == 'deleted':
            if request.user.is_anonymous:
                return Response({'details': 'Forbidden'}, status=status.HTTP_403_FORBIDDEN)
            if not request.user.is_staff:
                return Response({'details': 'Forbidden'}, status=status.HTTP_403_FORBIDDEN)
        return Response(self.serializer(help).data, status=status.HTTP_200_OK)
    
    @swagger_auto_schema(responses={
                            200: openapi.Response(
                                description='Успешно добавили',
                                schema=openapi.Schema(type=openapi.TYPE_OBJECT,
                                                      properties={
                                                          'lesion_information': openapi.Schema(
                                                                type=openapi.TYPE_OBJECT,
                                                                properties={
                                                                    'lesion_id': openapi.Schema(type=openapi.TYPE_NUMBER),
                                                                    'lesion_helps_count': openapi.Schema(type=openapi.TYPE_NUMBER)
                                                                })
                                                      })
                            ),
                            400: openapi.Response(
                                description='Не смогли добавить',
                                schema=error_schema
                            ),
                            403: openapi.Response(
                                description='Нет доступа',
                                schema=error_schema
                            )
    })
    @method_permission_classes([IsAuth])
    def post(self, request, help_id):
        lesion, is_created = Lesion.objects.get_or_create(
            creator = request.user,
            status = 'draft',
        )
        if Help_lesion.objects.filter(help=help_id, lesion=lesion.lesion_id).exists():
            return Response({'details': 'Уже добавлено'}, status=status.HTTP_400_BAD_REQUEST)
        else:
            Help_lesion.objects.create(
                lesion = Lesion.objects.get(lesion_id=lesion.lesion_id),
                help = Help.objects.get(help_id=help_id)
            )
            lesion_id = request.user.user_lesions.all().filter(status='draft').first().lesion_id
            lesion_helps_count = Help_lesion.objects.filter(lesion_id=lesion.lesion_id).count()
            return Response({'lesion_information': {'lesion_id': lesion_id, 'lesion_helps_count': lesion_helps_count}}, status=status.HTTP_200_OK)
    

    @swagger_auto_schema(request_body=serializer,
                         responses={
                            200: openapi.Response(
                                description='Успешное изменение услуги',
                                schema=HelpSerializer
                            ),
                            403: openapi.Response(
                                description='Нет доступа',
                                schema=error_schema
                            ),
                            404: openapi.Response(
                                description='Нет такой услуги',
                                schema=error_schema
                            )
    })
    @method_permission_classes([IsManager])
    def put(self, request, help_id):
        help = get_object_or_404(Help, pk=help_id)
        changed_help = self.serializer(help, request.data, partial=True)
        if changed_help.is_valid():
            changed_help.save()
            return Response(changed_help.data, status=status.HTTP_200_OK)
        return Response(changed_help.errors, status=status.HTTP_400_BAD_REQUEST)
    
    @swagger_auto_schema(responses={
                            200: openapi.Response(
                                description='Успешное изменение услуги',
                                schema=HelpSerializer
                            ),
                            403: openapi.Response(
                                description='Нет доступа',
                                schema=error_schema
                            ),
                            404: openapi.Response(
                                description='Нет такой услуги',
                                schema=error_schema
                            ),
                            400: openapi.Response(
                                description='Услуга уже удалена',
                                schema=error_schema
                            )
    })
    @method_permission_classes([IsManager])
    def delete(self, request, help_id):
        help = get_object_or_404(Help, pk=help_id)
        if help.status != '0':
            help.status = '0'
            if deleteImg(help.img_url) == 'success':
                help.img_url = ''
                help.save()
                return Response(self.serializer(help).data, status=status.HTTP_200_OK)
            help.save()
            return Response({'details': 'Удаление не удалось'}, status=status.HTTP_404_NOT_FOUND)
        return Response({'details': 'Элемент уже удален'}, status=status.HTTP_400_BAD_REQUEST)


@csrf_exempt
@swagger_auto_schema(method='post', 
                     consumes=['multipart/form-data'], 
                     request_body=openapi.Schema(
                        type=openapi.TYPE_OBJECT,
                        properties={
                            'img': openapi.Schema(type=openapi.TYPE_FILE)
                        },
                        required=['img']
                     ),
                     responses={
                        403: openapi.Response(
                            description='Нет доступа',
                            schema=error_schema
                        ),
                        202: openapi.Response(
                            description='Картинка успешно загружена',
                            schema=HelpSerializer
                        ),
                        400: openapi.Response(
                            description='Ошибка загрузки',
                            schema=error_schema
                        ),
                        404: openapi.Response(
                            description='Такой услуги нет',
                            schema=error_schema
                        )
})
@api_view(['post'])
@authentication_classes([AuthBySSID])
@permission_classes([IsManager])
def helpAddImg(request, help_id):
    help = get_object_or_404(Help, help_id=help_id)
    img = request.FILES.get('img')
    try:
        past_url = help.img_url
        help.img_url = addImg(img)
        dfg = deleteImg(past_url)
        help.save()
        return Response(HelpSerializer(help).data, status=status.HTTP_202_ACCEPTED)
    except:
        return Response({'details': 'Ошибка загрузки'}, status=status.HTTP_400_BAD_REQUEST)


class HelpLesionMethods(APIView):
    serializer = HelpLesionSerializer
    authentication_classes = [AuthBySSID]

    @swagger_auto_schema(responses={
                            404: openapi.Response(
                                description='Уже удалено/не существует',
                                schema=error_schema
                            ),
                            403: openapi.Response(
                                description='Нет доступа',
                                schema=error_schema
                            ),
                            200: openapi.Response(
                                description='Успешно удалено',
                                schema=HelpLesionSerializer(many=True)
                            )
    })
    @method_permission_classes([IsAuth])
    def delete(self, request, help_id, lesion_id):
        help_lesion = get_object_or_404(Help_lesion, help=help_id, lesion=lesion_id)
        help_lesion.delete()
        helps_lesion = Help_lesion.objects.filter(lesion=lesion_id)
        return Response(self.serializer(helps_lesion, many=True).data, status=status.HTTP_200_OK)

    @swagger_auto_schema(request_body=openapi.Schema(
                            type=openapi.TYPE_OBJECT,
                            properties={
                                'comment': openapi.Schema(type=openapi.TYPE_STRING)
                            },
                         ),
                         responses={
                            403: openapi.Response(
                                description='Нет доступа',
                                schema=error_schema
                            ),
                            404: openapi.Response(
                                description='Нет такого протокола помощи при этом поражении',
                                schema=error_schema
                            ),
                            200: openapi.Response(
                                description='Успешное изменение поля м-м',
                                schema=HelpLesionSerializer(many=True)
                            )
    })
    @permission_classes([IsAuth])
    def put(self, request, help_id, lesion_id):
        help_lesion = get_object_or_404(Help_lesion, help=help_id, lesion=lesion_id)
        changed_Help_lesion = self.serializer(help_lesion, data=request.data, partial=True) 
        if changed_Help_lesion.is_valid():
            changed_Help_lesion.save() 
            helps_lesion = Help_lesion.objects.filter(lesion=lesion_id)
            return Response(self.serializer(helps_lesion, many=True).data, status=status.HTTP_200_OK)
        return Response(changed_Help_lesion.errors, status=status.HTTP_400_BAD_REQUEST)

class lesionsMethods(APIView):
    serializer = LesionSerializer
    authentication_classes = [AuthBySSID]

    @swagger_auto_schema(manual_parameters=[
                            openapi.Parameter(
                                'start_date',
                                openapi.IN_QUERY,
                                description='Начальная дата',
                                type=openapi.TYPE_STRING
                            ),
                            openapi.Parameter(
                                'end_date',
                                openapi.IN_QUERY,
                                description='Конечная дата',
                                type=openapi.TYPE_STRING
                            ),
                            openapi.Parameter(
                                'status',
                                openapi.IN_QUERY,
                                description='Статус (completed/formed/rejected)',
                                type=openapi.TYPE_STRING
                            )
                         ],
                         responses={
                            403: openapi.Response(
                                description='Нет доступа',
                                schema=error_schema
                            ),
                            400: openapi.Response(
                                description='Неправильные фильтры',
                                schema=error_schema
                            ),
                            200: openapi.Response(
                                description='Успешное применение фильтра',
                                schema=LesionSerializer(many=True)
                            ),
    })
    @method_permission_classes([IsAuth])
    def get(self, request):
        acceptable_statuses = [
            'completed',
            'formed',
            'rejected'
        ]

        start_date = request.query_params.get('start_date')
        end_date = request.query_params.get('end_date')
        status_filter = request.query_params.get('status')

        if request.user.is_staff:
            lesions = Lesion.objects.filter(status__in=acceptable_statuses)
        else:
            lesions = Lesion.objects.filter(status__in=acceptable_statuses, creator=request.user)

        filter = {}
        if start_date:
            start_date = parse_datetime(start_date)
            if start_date is None:
                return Response({'details': 'start_date'}, status=status.HTTP_400_BAD_REQUEST)
            filter['date_of_creation__gte'] = start_date
        if end_date:
            end_date = parse_datetime(end_date)
            if end_date is None:
                return Response({'details': 'end_date'}, status=status.HTTP_400_BAD_REQUEST)
            filter['date_of_creation__lte'] = end_date
        if status_filter:
            if not status_filter in acceptable_statuses:
                return Response({'details': 'status'}, status=status.HTTP_400_BAD_REQUEST)
            filter['status'] = status_filter
        
        return Response(self.serializer(lesions.filter(**filter), many = True).data, status=status.HTTP_200_OK)
    
class lesionMethods(APIView):
    serializer = LesionSerializer
    authentication_classes = [AuthBySSID]

    @swagger_auto_schema(responses={
                            403: openapi.Response(
                                description='Нет доступа',
                                schema=error_schema
                            ),
                            404: openapi.Response(
                                description='Такого поражения не существует',
                                schema=error_schema
                            ),
                            200: openapi.Response(
                                description='Успешное получение критического поражения',
                                schema=LesionSerializer
                            ),
    })
    @method_permission_classes([IsAuth])
    def get(self, request, lesion_id):
        lesion = get_object_or_404(Lesion, lesion_id=lesion_id)
        if lesion.creator != request.user and not request.user.is_staff:
            return Response({'details:', 'Forbidden'}, status=status.HTTP_403_FORBIDDEN)
        return Response(self.serializer(lesion).data, status=status.HTTP_200_OK)
    
    @swagger_auto_schema(request_body=openapi.Schema(
                            type=openapi.TYPE_OBJECT,
                            properties={
                                'pass_time': openapi.Schema(type=openapi.TYPE_STRING)
                            } 
                         ),
                         responses={
                            403: openapi.Response(
                                description='Нет доступа',
                                schema=error_schema
                            ),
                            404: openapi.Response(
                                description='Нет такого поражения',
                                schema=error_schema
                            ),
                            200: openapi.Response(
                                description='Успешное изменение',
                                schema=ok_schema
                            )
    })
    @method_permission_classes([IsAuth])
    def put(self, request, lesion_id):
        lesion = get_object_or_404(lesion, creator = request.user, lesion_id=lesion_id)
        lesion.pass_time = request.data['pass_time']
        lesion.save()
        return Response({'status': 'ok'}, status=status.HTTP_200_OK)

class forminglesion(APIView):
    serializer = LesionSerializer
    authentication_classes = [AuthBySSID]

    @swagger_auto_schema(responses={
                            403: openapi.Response(
                                description='Нет доступа',
                                schema=error_schema
                            ),
                            400: openapi.Response(
                                description='Пустое(-ые) поля',
                                schema=error_schema
                            ),
                            404: openapi.Response(
                                description='Нет такого поражения',
                                schema=error_schema
                            ),
                            202: openapi.Response(
                                description='Успешное формирование заявки',
                                schema=LesionSerializer
                            ),
    })
    @method_permission_classes([IsAuth])
    def put(self, request, lesion_id):
        lesion = get_object_or_404(Lesion, creator = request.user, lesion_id=lesion_id)
        helps = lesion.lesion_helps.all()
        for help in helps:
            if help.comment is None or help.comment == '':
                return Response({'details': 'comment'}, status=status.HTTP_400_BAD_REQUEST)
        lesion.status = 'formed'
        lesion.date_of_formation = timezone.now()
        lesion.save()
        return Response(self.serializer(lesion).data, status=status.HTTP_202_ACCEPTED)
    
    @swagger_auto_schema(responses={
                            403: openapi.Response(
                                description='Нет доступа',
                                schema=error_schema
                            ),
                            404: openapi.Response(
                                description='Нет такого распада',
                                schema=error_schema
                            ),
                            202: openapi.Response(
                                description='Успешное удаление распада',
                                schema=LesionSerializer
                            ),
    })
    @method_permission_classes([IsAuth])
    def delete(self, request, lesion_id):
        lesion = get_object_or_404(Lesion, creator = request.user, lesion_id=lesion_id)
        lesion.status = 'deleted'
        lesion.date_of_formation = timezone.now()
        lesion.save()
        return Response(self.serializer(lesion).data, status=status.HTTP_202_ACCEPTED)

class moderatelesion(APIView):
    serializer = LesionSerializer
    authentication_classes = [AuthBySSID]

    @swagger_auto_schema(request_body=openapi.Schema(
                            type=openapi.TYPE_OBJECT,
                            properties={
                                'accept': openapi.Schema(type=openapi.TYPE_STRING)
                            },
                            required=['accept']
                         ),
                         responses={
                            403: openapi.Response(
                                description='Нет доступа',
                                schema=error_schema
                            ),
                            404: openapi.Response(
                                description='Нет такого поражения',
                                schema=error_schema
                            ),
                            400: openapi.Response(
                                description='Заявка не сформирована/неверное действие(accept)',
                                schema=error_schema
                            ),
                            202: openapi.Response(
                                description='Успешное отклонение',
                                schema=LesionSerializer
                            ),
    })
    @method_permission_classes([IsManager])
    def put(self, request, lesion_id):
        lesion = get_object_or_404(Lesion, pk=lesion_id)
        accept = request.data.get('accept')
        if lesion.status == 'formed':
            if accept == 'false':
                lesion.status = 'rejected'
                lesion.moderator = request.user
                lesion.date_of_finish = timezone.now()
                lesion.save()
                return Response(self.serializer(lesion).data, status=status.HTTP_202_ACCEPTED)
            elif accept == 'true':
                helps = lesion.lesion_helps.all()
                sum_duration = 0
                for help in helps:
                    sum_duration += help.help.duration
                lesion.sum_duration = sum_duration
                lesion.moderator = request.user
                lesion.status = 'completed'
                lesion.date_of_finish = timezone.now()
                lesion.qr = generate_lesion_qr(lesion)
                lesion.save()
                return Response(self.serializer(lesion).data, status=status.HTTP_202_ACCEPTED)
            else:
                return Response({'details': 'Неверное действие'}, status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response({'details': 'Заявка не сформирована'}, status=status.HTTP_400_BAD_REQUEST)

@csrf_exempt
@swagger_auto_schema(method='post',
                     request_body=SwaggerCustomUserSerializer,
                     responses={
                        400: openapi.Response(
                            description='Ошибка регистрации',
                            schema=error_schema
                        ),
                        200: openapi.Response(
                            description='Успешная регистрация',
                            schema=CustomUserSerializer
                        ),
})
@api_view(['post'])
@authentication_classes([])
@permission_classes([AllowAny])
def registration_view(request):
    if CustomUser.objects.filter(email=request.data['email']).exists():
        return Response({'details': 'email exist'}, status=status.HTTP_400_BAD_REQUEST)
    serializer = CustomUserSerializer(data=request.data)
    if serializer.is_valid():
        CustomUser.objects.create_user(email=serializer.data['email'],
                                       password=serializer.data['password'])
        user = authenticate(request, email=request.data['email'], password=request.data['password'])
        return Response(CustomUserSerializer(user).data, status=status.HTTP_200_OK)
    return Response({'details': 'registration failed'}, status=status.HTTP_400_BAD_REQUEST)

@swagger_auto_schema(method='put', 
                     request_body=openapi.Schema(
                        type=openapi.TYPE_OBJECT,
                        properties={
                            'email': openapi.Schema(type=openapi.TYPE_STRING),
                            'password': openapi.Schema(type=openapi.TYPE_STRING)
                        }
                     ),
                     responses={
                        403: openapi.Response(
                            description='Нет доступа',
                            schema=error_schema
                        ),
                        200: openapi.Response(
                            description='Нет доступа',
                            schema=CustomUserSerializer
                        ),
                     }
)
@api_view(['put'])
@authentication_classes([AuthBySSID])
@permission_classes([IsAuth])
def account_view(request):
    email = request.data.get("email")
    password = request.data.get("password")
    if email:
        ssid = request.COOKIES.get('session_id')
        try:
            session_storage.set(ssid, email)
        except Exception:
            return Response({'details': 'Session not found'}, status=status.HTTP_400_BAD_REQUEST)
        request.user.email = email
        request.user.save()
    if password:
        request.user.set_password(password)
        request.user.save()
        authenticate(request, email=request.user.email, password=password)
    return Response(CustomUserSerializer(request.user).data, status=status.HTTP_200_OK)

class attributeListMethods(APIView):
    authentication_classes = [AuthBySSID]

    @swagger_auto_schema(request_body=openapi.Schema(type=openapi.TYPE_OBJECT,
                                                     properties={
                                                         'name': openapi.Schema(type=openapi.TYPE_STRING),
                                                         'value': openapi.Schema(type=openapi.TYPE_STRING)
                                                     },
                                                     required=['name']),
                        responses={
                            200: openapi.Response(
                                description='Успешное создании атрибута',
                                schema=AttributeHelpSerializer
                            )
                        })
    @method_permission_classes([IsManager])
    def post(self, request, help_id):
        attribute_name = request.data.get('name', '')
        attribute_value = request.data.get('value', '')
        help = get_object_or_404(Help, pk=help_id)
        if Attribute.objects.filter(name=attribute_name).exists():
            attribute = Attribute.objects.get(name=attribute_name)
        else:
            attribute = Attribute.objects.create(name=attribute_name)
        help_attribute, created = Attribute_help.objects.get_or_create(help=help, attribute=attribute)
        help_attribute.value = attribute_value
        help_attribute.save()
        return Response(AttributeHelpSerializer(help_attribute).data, status=status.HTTP_200_OK)
    
    @swagger_auto_schema(responses={
                            200: openapi.Response(
                                description='Успешное получение атрибутов',
                                schema=HelpForAttributesSerializer
                            )
                        })
    @method_permission_classes([AllowAny])
    def get(self, request, help_id):
        help = get_object_or_404(Help, pk=help_id)
        return Response(HelpForAttributesSerializer(help).data, status=status.HTTP_200_OK)
        
class attributeDetailMethods(APIView):
    authentication_classes = [AuthBySSID]

    @swagger_auto_schema(responses={
                            200: openapi.Response(
                                description='Успешное удаление атрибута',
                                schema=openapi.Schema(type=openapi.TYPE_OBJECT,
                                                      properties={
                                                          'id': openapi.Schema(type=openapi.TYPE_NUMBER)
                                                      })
                            ),
                        })
    @method_permission_classes([IsManager])
    def delete(self, request, help_id, attribute_id):
        help = get_object_or_404(help, pk=help_id)
        attribute = get_object_or_404(Attribute, pk=attribute_id)
        get_object_or_404(Attribute_help, attribute=attribute, help=help).delete()
        return Response({'id': attribute.attribute_id}, status=status.HTTP_200_OK)
    
    @swagger_auto_schema(request_body=openapi.Schema(type=openapi.TYPE_OBJECT,
                                                     properties={
                                                         'value': openapi.Schema(type=openapi.TYPE_STRING)
                                                     }),
                        responses={
                            200: openapi.Response(
                                description='Успешное создании атрибута',
                                schema=ok_schema
                            )
                        })
    @method_permission_classes([IsManager])
    def put(self, request, help_id, attribute_id):
        help = get_object_or_404(Help, pk=help_id)
        attribute = get_object_or_404(Attribute, pk=attribute_id)
        value = request.data.get('value', '')
        help_attribute = get_object_or_404(Attribute_help, attribute=attribute, help=help)
        help_attribute.value = value
        help_attribute.save()
        return Response({'status': 'ok'}, status=status.HTTP_200_OK)
        
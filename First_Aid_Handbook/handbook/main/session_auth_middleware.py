# main/session_auth_middleware.py
from django.utils.deprecation import MiddlewareMixin
from django.contrib.auth.models import AnonymousUser
import redis
from django.conf import settings
from .models import CustomUser  # Импорт вашей кастомной модели пользователя

# Подключение к Redis
session_storage = redis.StrictRedis(
    host=settings.REDIS_HOST,
    port=settings.REDIS_PORT
)

class SessionAuthMiddleware(MiddlewareMixin):
    def process_request(self, request):
        # Получаем session_id из кук
        session_id = request.COOKIES.get('session_id')
        
        if session_id:
            try:
                # Получаем email из Redis
                email_bytes = session_storage.get(session_id)
                
                if email_bytes:
                    email = email_bytes.decode('utf-8')
                    # Ищем пользователя в БД
                    user = CustomUser.objects.get(email=email)
                    request.user = user
                else:
                    request.user = AnonymousUser()
                    
            except CustomUser.DoesNotExist:
                request.user = AnonymousUser()
        else:
            request.user = AnonymousUser()
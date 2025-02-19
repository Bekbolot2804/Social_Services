from django.urls import path, include
from main import views
from rest_framework import routers  # Импортируем модуль routers
from drf_yasg.views import get_schema_view
from drf_yasg import openapi
from main.permissions import permissions
from main.views import UserViewSet

# Создаем экземпляр DefaultRouter или SimpleRouter
router = routers.DefaultRouter()  # Используем DefaultRouter

# Регистрируем viewset в роутере
router.register(r'user', UserViewSet, basename='user')

# Создаем схему Swagger
schema_view = get_schema_view(
    openapi.Info(
        title="Snippets API",
        default_version='v1',
        description="Test description",
        terms_of_service="https://www.google.com/policies/terms/",
        contact=openapi.Contact(email="contact@snippets.local"),
        license=openapi.License(name="BSD License"),
    ),
    public=True,
    permission_classes=(permissions.AllowAny,),
)

urlpatterns = [
    # Роуты для API
    path('user', include(router.urls)),  # Включаем URL-шаблоны, зарегистрированные в router

    # Другие URL-шаблоны
    path('helps/', views.HelpView.as_view()),
    path('helps/<int:pk>/', views.HelpDetailView.as_view()),
    path('helps/<int:pk>/image/', views.ImageUploadView.as_view()),
    path('api-auth/', include('rest_framework.urls', namespace='rest_framework')),
    path('login', views.login_view, name='login'),
    path('logout', views.logout_view, name='logout'),
    path('lesions/', views.LesionView.as_view()),
    path('lesions/<int:pk>/', views.LesionDetailView.as_view()),
    path('lesions/draft/', views.LesionDraftView.as_view()),
    path('swagger/', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
    path('lesions/<int:lesion_id>/helps/', views.HelpLesionView.as_view()),
    path('lesions/<int:lesion_id>/helps/<int:help_id>/', views.HelpLesionView.as_view()),
]
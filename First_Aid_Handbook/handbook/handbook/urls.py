from django.urls import path
from main.views import UserRegistration, LoginView, LogoutView  # Добавьте этот импорт
from main import views
from rest_framework import permissions
from django.urls import path, include
from drf_yasg.views import get_schema_view
from drf_yasg import openapi

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
    path('register/', UserRegistration.as_view()),
    path('login/', LoginView.as_view()),
    path('logout/', LogoutView.as_view()),
    path('helps/', views.HelpView.as_view()),
    path('helps/<int:pk>/', views.HelpDetailView.as_view()),
    path('helps/<int:pk>/image/', views.ImageUploadView.as_view()),
    path('swagger/', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
    path('lesions/', views.LesionView.as_view()),
    path('lesions/<int:pk>/', views.LesionDetailView.as_view()),
    path('lesions/draft/', views.LesionDraftView.as_view()),
    
    path('lesions/<int:lesion_id>/helps/', views.HelpLesionView.as_view()),
    path('lesions/<int:lesion_id>/helps/<int:help_id>/', views.HelpLesionView.as_view()),
]
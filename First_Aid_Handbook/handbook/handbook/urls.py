"""
URL configuration for bmstu_lab project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path

from main import views
from rest_framework.authtoken.views import obtain_auth_token  # Импортируйте встроенное представление


urlpatterns = [
    path('admin/', admin.site.urls),
    path('helps', views.HelpList.as_view()),
    path('helps/<int:pk>', views.HelpDetail.as_view()),
    path('lesions/', views.LesionView.as_view()),
    path('lesions/<int:pk>/', views.LesionView.as_view()),
    path('lesions/<int:lesion_id>/helps/', views.HelpLesionView.as_view()),
    path('lesions/<int:lesion_id>/helps/<int:help_id>/', views.HelpLesionView.as_view()),
    path('register/', views.UserRegisterView.as_view()),
    path('users/<int:pk>/', views.UserProfileView.as_view()),
    path('lesions/create/', views.LesionCreateView.as_view(), name='lesion-create'),
    path('api-token-auth/', obtain_auth_token, name='api_token_auth'), 
]
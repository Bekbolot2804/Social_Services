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
# Обновленные URL
from django.urls import path
from main import views

urlpatterns = [
    path('api/helps/', views.HelpView.as_view(), name='help-list'),
    path('api/lesions/', views.LesionView.as_view(), name='lesion-list'),
    path('api/help-lesions/', views.HelpLesionView.as_view(), name='help-lesion-list'),

    # Дополнительные пути, восстановленные из исходного файла
    path('api/helps/<int:id>/', views.HelpView.as_view(), name='help-detail'),
    path('api/lesions/<int:id>/', views.LesionView.as_view(), name='lesion-detail'),
    path('api/help-lesions/<int:id>/', views.HelpLesionView.as_view(), name='help-lesion-detail'),

    # Пользовательские маршруты для дополнительных функций
    path('api/lesions/<int:id>/status/', views.LesionStatusUpdateView.as_view(), name='lesion-status-update'),
    path('api/help-lesions/<int:id>/time/', views.HelpLesionTimeUpdateView.as_view(), name='help-lesion-time-update'),

    # Пример авторизации
    path('api/auth/login/', views.UserLoginView.as_view(), name='user-login'),
    path('api/auth/logout/', views.UserLogoutView.as_view(), name='user-logout'),
]

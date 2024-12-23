from django.contrib import admin
from main import views
from django.urls import include, path
from rest_framework import routers

routers = routers.DefaultRouter()

urlpatterns = [
    path('', include(routers.urls)),
    path(r'users/', views.UsersList.as_view(), name='users-list'),
    path(r'helps/', views.HelpList.as_view(), name='stocks-list'),
    path(r'helps/<int:pk>/', views.HelpDetail.as_view(), name='stocks-detail'),
    path(r'helps/<int:pk>/put/', views.put, name='stocks-put'),
    path(r'lesions/', views.LesionList.as_view(), name='stocks-list'),
    path(r'lesions/<int:pk>/', views.LesionDetail.as_view(), name='stocks-detail'),
    path(r'lesions/<int:pk>/put/', views.put, name='stocks-put'),
    path('api-auth/', include('rest_framework.urls', namespace='rest_framework')),
    path('admin/', admin.site.urls),
]
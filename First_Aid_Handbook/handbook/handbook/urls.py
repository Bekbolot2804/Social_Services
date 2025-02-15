from django.urls import path
from main.views import UserRegistration, LoginView, LogoutView  # Добавьте этот импорт
from main import views

urlpatterns = [
    path('register/', UserRegistration.as_view()),
    path('login/', LoginView.as_view()),
    path('logout/', LogoutView.as_view()),
    path('helps/', views.HelpView.as_view()),
    path('helps/<int:pk>/', views.HelpDetailView.as_view()),
    path('helps/<int:pk>/image/', views.ImageUploadView.as_view()),
    
    path('lesions/', views.LesionView.as_view()),
    path('lesions/<int:pk>/', views.LesionDetailView.as_view()),
    path('lesions/draft/', views.LesionDraftView.as_view()),
    
    path('lesions/<int:lesion_id>/helps/', views.HelpLesionView.as_view()),
    path('lesions/<int:lesion_id>/helps/<int:help_id>/', views.HelpLesionView.as_view()),
]
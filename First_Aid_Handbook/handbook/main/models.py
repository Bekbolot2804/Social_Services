from django.db import models
from django.contrib.auth.models import AbstractUser
from handbook import settings
from django.contrib.auth.models import UserManager
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin

class NewUserManager(UserManager):
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError('Users must have an email address')
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self.db)
        return user

class CustomUser(AbstractBaseUser, PermissionsMixin):
    email = models.EmailField(("email адрес"), unique=True)
    password = models.CharField(max_length=50, verbose_name="Пароль")    
    is_staff = models.BooleanField(default=False, verbose_name="Является ли пользователь менеджером?")
    is_superuser = models.BooleanField(default=False, verbose_name="Является ли пользователь админом?")

    USERNAME_FIELD = 'email'

    objects =  NewUserManager()
# class CustomUser(AbstractUser):
#     is_moderator = models.BooleanField(default=False)
    
#     class Meta:
#         swappable = 'AUTH_USER_MODEL'  # Корректная настройка для заменяемой модели

class Help(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField()
    duration = models.PositiveIntegerField()
    image_url = models.URLField(null=True, blank=True)
    is_active = models.BooleanField(default=True)

class Lesion(models.Model):
    STATUS_CHOICES = [
        ('draft', 'Черновик'),
        ('formed', 'Сформирована'),
        ('completed', 'Завершена'),
        ('rejected', 'Отклонена'),
        ('deleted', 'Удалена'),
    ]
    
    name = models.CharField(max_length=100)
    creator = models.ForeignKey(
        settings.AUTH_USER_MODEL, 
        on_delete=models.CASCADE,
        related_name='created_lesions'
    )
    moderator = models.ForeignKey(
        settings.AUTH_USER_MODEL, 
        null=True, 
        blank=True, 
        on_delete=models.SET_NULL,
        related_name='moderated_lesions'
    )
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='draft')
    created_at = models.DateTimeField(auto_now_add=True)
    formed_at = models.DateTimeField(null=True, blank=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    total_cost = models.DecimalField(max_digits=10, decimal_places=2, default=0)

class HelpLesion(models.Model):
    help = models.ForeignKey(Help, on_delete=models.CASCADE)
    lesion = models.ForeignKey(Lesion, on_delete=models.CASCADE, related_name='help_lesions')
    quantity = models.PositiveIntegerField(default=1)
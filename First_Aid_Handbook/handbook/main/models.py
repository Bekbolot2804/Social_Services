from django.db import models
from django.contrib.auth.models import AbstractUser
from django.conf import settings  # Правильно

class CustomUser(AbstractUser):
    is_moderator = models.BooleanField(default=False)
    is_staff = models.BooleanField(default=False)
    
    class Meta:
        swappable = 'AUTH_USER_MODEL'

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
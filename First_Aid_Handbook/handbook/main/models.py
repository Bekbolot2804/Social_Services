from django.db import models
from django.contrib.auth.models import User
from django.contrib.auth.models import AbstractUser
from handbook.settings import AUTH_USER_MODEL

class CustomUser(AbstractUser):
    is_moderator = models.BooleanField(default=False)
    # Указываем уникальные related_name
    groups = models.ManyToManyField(
        'auth.Group',
        verbose_name='groups',
        blank=True,
        help_text='The groups this user belongs to.',
        related_name='customuser_set',  # Уникальное имя
        related_query_name='customuser',
    )
    user_permissions = models.ManyToManyField(
        'auth.Permission',
        verbose_name='user permissions',
        blank=True,
        help_text='Specific permissions for this user.',
        related_name='customuser_set',  # Уникальное имя
        related_query_name='customuser',
    )

class Help(models.Model):
    name = models.CharField(max_length=100, verbose_name="Вид помощи")
    description = models.TextField(verbose_name="Описание методики")
    image = models.CharField(max_length=255, blank=True, null=True)
    title = models.CharField(max_length=100, blank=True, null=True)  # Добавьте это поле
    duration = models.PositiveIntegerField(verbose_name="Время оказания (мин)")
    is_deleted = models.BooleanField(default=False)

    def __str__(self):
        return self.name

class Lesion(models.Model):
    STATUS_CHOICES = [
        ('draft', 'Черновик'),
        ('formed', 'Сформирована'),
        ('completed', 'Завершена'),
        ('rejected', 'Отклонена'),
        ('deleted', 'Удалена'),
    ]
    
    name = models.CharField(max_length=100, verbose_name="Вид поражения")
    name = models.CharField(max_length=100, verbose_name="Вид поражения")
    creator = models.ForeignKey(
        AUTH_USER_MODEL,  # Используем AUTH_USER_MODEL
        on_delete=models.CASCADE,
        related_name='created_lesions',
        null=True,
        blank=True
    )
    moderator = models.ForeignKey(
        AUTH_USER_MODEL,  # Используем AUTH_USER_MODEL
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='moderated_lesions'
    )
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='draft')
    created_at = models.DateTimeField(auto_now_add=True)
    date_formed = models.DateTimeField(null=True, blank=True)
    date_completed = models.DateTimeField(null=True, blank=True)
    disaster_type = models.CharField(max_length=100, verbose_name="Тип ЧС")
    total_cost = models.DecimalField(max_digits=10, decimal_places=2, default=0)

    def total_duration(self):
        return sum(hl.help.duration for hl in self.help_lesions.all())

class HelpLesion(models.Model):
    help = models.ForeignKey(Help, on_delete=models.CASCADE, related_name='help_lesions')
    lesion = models.ForeignKey(Lesion, on_delete=models.CASCADE, related_name='help_lesions')
    application_order = models.PositiveIntegerField(verbose_name="Порядок применения")
    notes = models.TextField(blank=True, verbose_name="Особенности применения")
    quantity = models.PositiveIntegerField(default=1)
    class Meta:
        ordering = ['application_order']
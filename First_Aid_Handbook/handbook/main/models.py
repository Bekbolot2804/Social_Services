from django.db import models
from django.contrib.auth.models import User

# Исправленные и обновленные модели "Помощь"
class Help(models.Model):
    name = models.CharField(max_length=50, verbose_name="Название")
    image = models.ImageField(upload_to='images/', verbose_name="Изображение") 
    title = models.CharField(max_length=120, verbose_name="Заголовок")
    description = models.TextField(verbose_name="Описание")  # Исправлено на TextField для длинного текста

    def __str__(self):
        return self.name

# Модель "Поражение"
class Lesion(models.Model):
    status_choices = [  # Добавлены фиксированные варианты для статуса
        ('active', 'Активно'),
        ('resolved', 'Решено'),
        ('pending', 'В ожидании'),
    ]

    name = models.CharField(max_length=50, verbose_name="Название поражения")
    client = models.ForeignKey(User, on_delete=models.DO_NOTHING, null=True, related_name='client_lesions', verbose_name="Клиент")
    helper = models.ForeignKey(User, on_delete=models.DO_NOTHING, null=True, related_name='helper_lesions', verbose_name="Помощник")
    status = models.CharField(max_length=20, choices=status_choices, verbose_name="Статус")  # Добавлен choices
    date_start = models.DateTimeField(null=True, blank=True, verbose_name="Дата начала")
    date_end = models.DateTimeField(null=True, blank=True, verbose_name="Дата завершения")
    date_applied = models.DateTimeField(null=True, blank=True, verbose_name="Дата подачи заявки")

    def __str__(self):
        return self.name

# Модель "Помощь при поражении"
class HelpLesion(models.Model):
    help = models.ForeignKey(Help, on_delete=models.CASCADE, related_name='help_lesions', verbose_name="Помощь")
    lesion = models.ForeignKey(Lesion, on_delete=models.CASCADE, related_name='lesion_helps', verbose_name="Поражение")
    time = models.DurationField(null=True, blank=True, verbose_name="Продолжительность")  # Исправлено на DurationField
    comment = models.TextField(blank=True, verbose_name="Комментарий")  # Исправлено на TextField для длинного текста

    def __str__(self):
        return f"{self.help} для {self.lesion}"
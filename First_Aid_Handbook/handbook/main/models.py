from django.db import models
from django.contrib.auth.models import User


# Модель "Помощь"
class Help(models.Model):
    name = models.CharField(max_length=50, verbose_name="Название")
    image = models.CharField(max_length=255, blank=True, null=True, verbose_name="URL изображения")
    title = models.CharField(max_length=120, verbose_name="Заголовок")
    description = models.CharField(max_length=520, verbose_name="Описание")


    def __str__(self):
        return self.name

# Модель "Поражение"
class Lesion(models.Model):
    name = models.CharField(max_length=50, verbose_name="Название поражения")
    client = models.ForeignKey(User, on_delete=models.DO_NOTHING, null=True, related_name='client_lesions', verbose_name="Клиент")
    helper = models.ForeignKey(User, on_delete=models.DO_NOTHING, null=True, related_name='helper_lesions', verbose_name="Помощник")
    status = models.CharField(max_length=20, verbose_name="Статус")
    date_start = models.DateTimeField(null=True, blank=True, verbose_name="Дата начала")
    date_end = models.DateTimeField(null=True, blank=True, verbose_name="Дата завершения")
    date_applied = models.DateTimeField(null=True, blank=True, verbose_name="Дата подачи заявки")


    def __str__(self):
        return self.name

# Модель "Помощь при поражении"
class HelpLesion(models.Model):
    help = models.ForeignKey(Help, on_delete=models.CASCADE, related_name='help_lesions', verbose_name="Помощь")
    lesion = models.ForeignKey(Lesion, on_delete=models.CASCADE, related_name='lesion_helps', verbose_name="Поражение")
    time = models.TimeField(null=True, blank=True, verbose_name="Время")
    comment = models.CharField(max_length=249, verbose_name="Комментарий")


    def __str__(self):
        return f"{self.help} для {self.lesion}"

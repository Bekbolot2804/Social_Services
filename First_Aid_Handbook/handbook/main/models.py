from django.db import models

class AuthUser(models.Model):
    password = models.CharField(max_length=128)
    last_login = models.DateTimeField(blank=True, null=True)
    is_superuser = models.BooleanField(default=False)
    username = models.CharField(unique=True, max_length=150)
    last_name = models.CharField(max_length=150)
    email = models.CharField(max_length=254)
    is_staff = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    date_joined = models.DateTimeField(auto_now=True)
    first_name = models.CharField(max_length=150)

    def _str_(self):
        return f'{self.first_name}{self.last_name}'
    
    class Meta:
        managed = False
        db_table = 'auth_user'

# Модель "Помощь"
class Help(models.Model):
    name = models.CharField(max_length=50, verbose_name="Название")
    title = models.CharField(max_length=120, verbose_name="Заголовок")
    description = models.CharField(max_length=520, verbose_name="Описание")
    url = models.CharField(max_length=255, blank=True, null=True, verbose_name="Фото логотипа компании")
    user = models.ForeignKey('AuthUser', on_delete=models.DO_NOTHING, null=True, blank=False, verbose_name="Создатель акции")

# Модель "Поражение"
class Lesion(models.Model):
    name = models.CharField(max_length=50, verbose_name="Название поражения")
    creator = models.ForeignKey(AuthUser, on_delete=models.DO_NOTHING, null=True, blank=True, related_name='creator_lesions', verbose_name="Создатель")
    moderator = models.ForeignKey(AuthUser, on_delete=models.DO_NOTHING, null=True, blank=True, related_name='moderator_lesions', verbose_name="Модератор")
    status = models.CharField(max_length=20, verbose_name="Статус")
    date_start = models.DateTimeField(null=True, blank=True, verbose_name="Дата начала")
    date_end = models.DateTimeField(null=True, blank=True, verbose_name="Дата завершения")
    date_applied = models.DateTimeField(null=True, blank=True, verbose_name="Дата подачи заявки")

# Модель "Помощь при поражении"
class HelpLesion(models.Model):
    help = models.ForeignKey(Help, on_delete=models.CASCADE, related_name='help_lesions', verbose_name="Помощь")
    lesion = models.ForeignKey(Lesion, on_delete=models.CASCADE, related_name='lesion_helps', verbose_name="Поражение")
    time = models.TimeField(null=True, blank=True, verbose_name="Время")
    comment = models.CharField(max_length=249, verbose_name="Комментарий")

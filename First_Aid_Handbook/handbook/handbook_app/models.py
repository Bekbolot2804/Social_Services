from django.db import models
from django.contrib.auth import get_user_model
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin, UserManager
from django.contrib.auth.models import Group, Permission
from django.dispatch import receiver
from django.db.models.signals import post_save

class NewUserManager(UserManager):
    def create_user(self,email,password=None, **extra_fields):
        if not email:
            raise ValueError('User must have an email address')
        
        email = self.normalize_email(email) 
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self.db)
        return user

class CustomUser(AbstractBaseUser, PermissionsMixin):
    email = models.EmailField(("email адрес"), unique=True)
    password = models.CharField(max_length=254, verbose_name="Пароль")    
    is_staff = models.BooleanField(default=False, verbose_name="Является ли пользователь менеджером?")
    is_superuser = models.BooleanField(default=False, verbose_name="Является ли пользователь админом?")

    USERNAME_FIELD = 'email'

    objects =  NewUserManager()
    groups = models.ManyToManyField(
        Group,
        related_name='customuser_groups', 
        blank=True,
        verbose_name='Группы'
    )

    user_permissions = models.ManyToManyField(
        Permission,
        related_name='customuser_permissions',
        blank=True,
        verbose_name='Разрешения'
    )

class Help(models.Model):
    status_choices = [
        ('active', 'действует'),
        ('deleted', 'удален')
    ]

    help_id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=30)
    description = models.TextField()
    status = models.CharField(max_length=20, choices=status_choices)
    img_url = models.CharField(max_length=100, null=True, blank=True)
    duration = models.IntegerField()

class Lesion(models.Model):
    status_choices = [
        ('draft', 'черновик'),
        ('deleted', 'удален'),
        ('completed', 'завершен'),
        ('formed', 'сформирован'),
        ('rejected', 'отклонен')
    ]

    lesion_id = models.AutoField(primary_key=True)
    status = models.CharField(max_length=20, choices=status_choices)
    date_of_creation = models.DateTimeField(auto_now_add=True)
    creator = models.ForeignKey(get_user_model(), on_delete=models.DO_NOTHING, related_name='user_lesions')
    date_of_formation = models.DateTimeField(null=True, blank=True)
    date_of_finish = models.DateTimeField(null=True, blank=True)
    pass_time = models.CharField(max_length=30, null=True, blank=True)
    moderator = models.ForeignKey(get_user_model(), on_delete=models.DO_NOTHING, related_name='moderator_lesions', null=True, blank=True)
    qr = models.TextField(null=True)

class Help_lesion(models.Model):
    help = models.ForeignKey(Help, on_delete=models.DO_NOTHING, related_name='Help_lesions')
    lesion = models.ForeignKey(Lesion, on_delete=models.DO_NOTHING, related_name='lesion_helps')
    quantity = models.CharField(max_length=30, null=True, blank=True)
    remaining_quantity = models.CharField(max_length=40, null=True, blank=True)
    class Meta:
        unique_together = ('help', 'lesion')

class Attribute(models.Model):
    attribute_id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=30)

class Attribute_help(models.Model):
    help = models.ForeignKey(Help, on_delete=models.DO_NOTHING, related_name='help_attributes')
    attribute = models.ForeignKey(Attribute, on_delete=models.DO_NOTHING, related_name='attribute_helps')
    value = models.CharField(max_length=70, null=True, blank=True)

@receiver(post_save, sender=Attribute)
def create_attribute_helps(sender, instance, created, **kwargs):
    if created:
        helps = Help.objects.all()
        for help in helps:
            Attribute_help.objects.get_or_create(help=help, attribute=instance)

@receiver(post_save, sender=help)
def create_help_attributes(sender, instance, created, **kwargs):
    if created:
        attributes = Attribute.objects.all()
        for attribute in attributes:
            Attribute_help.objects.get_or_create(help=instance, attribute=attribute)
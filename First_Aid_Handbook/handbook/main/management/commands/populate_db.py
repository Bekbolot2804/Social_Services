from django.core.management.base import BaseCommand
from django.contrib.auth.hashers import make_password
from main.models import Help, Lesion, HelpLesion, CustomUser

class Command(BaseCommand):  # <-- Обязательное наследование от BaseCommand
    help = 'Populate database with initial data'

    def handle(self, *args, **options):
        # Создаем пользователя
        user, created = CustomUser.objects.get_or_create(
            username="admin",
            defaults={
                'email': 'admin@example.com',
                'password': make_password('admin123'),
                'is_staff': True,
                'is_superuser': True
            }
        )
        
        # Создаем объекты
        help_obj = Help.objects.create(
            title="Первая помощь при ожогах",
            description="Охладить место ожога...",
            price=0,
            creator=user
        )
        
        lesion_obj = Lesion.objects.create(
            title="Ожог",
            description="Термическое повреждение..."
        )
        
        HelpLesion.objects.create(
            help=help_obj,
            lesion=lesion_obj
        )
        
        self.stdout.write(self.style.SUCCESS("Данные успешно добавлены!"))
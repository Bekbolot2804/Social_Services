# populate_db.py
from django.contrib.auth.hashers import make_password
from main.models import CustomUser, Help, Lesion, HelpLesion
from django.utils import timezone

def run():
    # Создаем пользователей
    moderator = CustomUser.objects.create(
        username='moderator1',
        email='moder@example.com',
        password=make_password('moderpass123'),
        is_moderator=True
    )
    
    staff_user = CustomUser.objects.create(
        username='staff1',
        email='staff@example.com',
        password=make_password('staffpass123'),
        is_staff=True
    )

    creator1 = CustomUser.objects.create(
        username='creator1',
        email='creator1@example.com',
        password=make_password('creator123')
    )

    # Создаем виды помощи
    help_data = [
        {
            'name': 'Остановка кровотечения',
            'description': 'Наложение жгута или давящей повязки',
            'duration': 15,
            'image_url': 'https://example.com/bleeding.jpg'
        },
        {
            'name': 'Иммобилизация переломов',
            'description': 'Наложение шины на поврежденную конечность',
            'duration': 30,
            'image_url': 'https://example.com/fracture.jpg'
        },
        {
            'name': 'Сердечно-легочная реанимация',
            'description': 'Проведение базовой СЛР',
            'duration': 45,
            'image_url': None
        }
    ]

    helps = []
    for item in help_data:
        helps.append(Help(**item))
    Help.objects.bulk_create(helps)

    # Создаем поражения
    lesion1 = Lesion.objects.create(
        name='Открытый перелом бедра',
        creator=creator1,
        moderator=moderator,
        status='formed',
        created_at=timezone.now() - timezone.timedelta(days=3),
        formed_at=timezone.now() - timezone.timedelta(days=2),
        total_cost=2500.00
    )

    lesion2 = Lesion.objects.create(
        name='Ожог 2 степени 15% тела',
        creator=creator1,
        status='draft',
        created_at=timezone.now() - timezone.timedelta(hours=2))
    
    # Создаем связи между услугами и поражениями
    HelpLesion.objects.create(
        help=Help.objects.get(name='Остановка кровотечения'),
        lesion=lesion1,
        quantity=2
    )

    HelpLesion.objects.create(
        help=Help.objects.get(name='Иммобилизация переломов'),
        lesion=lesion1,
        quantity=1
    )

    HelpLesion.objects.create(
        help=Help.objects.get(name='Сердечно-легочная реанимация'),
        lesion=lesion2,
        quantity=3
    )

    print("База данных успешно заполнена!")
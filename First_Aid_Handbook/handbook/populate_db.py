import random
from django.contrib.auth import get_user_model
from main.models import Help, Lesion, HelpLesion
from django.utils import timezone

# Создание пользователей
def create_users():
    User = get_user_model()
    users_data = [
        {"email": "user1@example.com", "password": "user123"},
        {"email": "user2@example.com", "password": "user123"},
        {"email": "moderator@example.com", "password": "mod123"},
    ]

    users = []
    for data in users_data:
        user = User.objects.create_user(
            email=data["email"],
            password=data["password"]
        )
        users.append(user)
        print(f"Создан пользователь: {user.email}")
    return users

# Заполнение данных для Help
def create_helps():
    helps_data = [
        {"name": "Первая помощь при ожогах", "description": "Как обработать ожог.", "duration": 10},
        {"name": "Первая помощь при травмах", "description": "Как оказать помощь при травмах.", "duration": 15},
        {"name": "Первая помощь при удушье", "description": "Методы оказания помощи при удушье.", "duration": 5},
    ]

    for data in helps_data:
        help_obj = Help.objects.create(**data)
        print(f"Создана запись Help: {help_obj.name}")

# Заполнение данных для Lesion
def create_lesions(users):
    statuses = ['draft', 'formed', 'completed', 'rejected', 'deleted']
    lesions_data = [
        {"name": "Перелом руки"},
        {"name": "Ожог второй степени"},
        {"name": "Отравление ядовитыми веществами"},
        {"name": "Ушиб колена"},
        {"name": "Кровотечение из носа"},
    ]

    for data in lesions_data:
        creator = random.choice(users)  # Случайный выбор создателя из списка пользователей
        lesion_obj = Lesion.objects.create(
            name=data["name"],
            status=random.choice(statuses),
            creator=creator,
            created_at=timezone.now(),
            total_cost=round(random.uniform(100.00, 1000.00), 2)
        )
        print(f"Создана запись Lesion: {lesion_obj.name} со статусом {lesion_obj.status}, создатель: {creator.email}")

# Заполнение данных для HelpLesion
def create_help_lesions():
    helps = list(Help.objects.all())
    lesions = list(Lesion.objects.all())

    if not helps or not lesions:
        print("Необходимо сначала создать записи для Help и Lesion.")
        return

    for lesion in lesions:
        related_helps = random.sample(helps, k=random.randint(1, len(helps)))
        for help_obj in related_helps:
            HelpLesion.objects.create(
                help=help_obj,
                lesion=lesion,
                quantity=random.randint(1, 5)
            )
            print(f"Связана помощь {help_obj.name} с поражением {lesion.name}, количество: {random.randint(1, 5)}")

# Основной метод для выполнения всех операций
def populate_database():
    print("Заполнение данных для пользователей...")
    users = create_users()

    print("Заполнение данных для Help...")
    create_helps()

    print("Заполнение данных для Lesion...")
    create_lesions(users)

    print("Заполнение данных для HelpLesion...")
    create_help_lesions()

    print("База данных успешно заполнена!")

if __name__ == "__main__":
    populate_database()
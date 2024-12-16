from django.shortcuts import render, redirect, get_object_or_404
from django.utils import timezone
from django.db import connection
from .models import Help, Lesion, HelpLesion
from django.db.models import Q


def get_helps(request):
    # Получаем заявку с фиксированным id=1
    lesion = Lesion.objects.filter(id=1).first()

    # Если заявки с id=1 нет, создаем её
    if not lesion:
        lesion = Lesion.objects.create(
            id=1,  # фиксированный id
            client=request.user,
            name="Основная заявка",
            status='draft',
            date_applied=timezone.now()
        )
        print(f"Создана новая заявка с фиксированным ID: {lesion.id}")

    # Получаем все связи с 'HelpLesion', связанные с текущей заявкой
    relations = HelpLesion.objects.select_related('help', 'lesion').filter(lesion=lesion)
    input_text = request.GET.get('text', "").lower()
    # Считаем количество связей
    count = relations.count()
    if input_text:
        matched_helps = Help.objects.filter(name__icontains=input_text)
    else:
        matched_helps = Help.objects.all()
    
    return render(request, 'helps.html', {
        'input_text': input_text,
        'helps': matched_helps,
        'lesions': [lesion],  # Передаём текущую заявку
        'relations': relations,
        'count': count,
    })

def get_help(request, id):
    help_instance = get_object_or_404(Help, pk=id)
    context = {
        'help': help_instance
    }
    return render(request, 'help.html', context)

def add_help_to_lesion(request):
    if request.method == 'POST':
        help_id = request.POST.get('addingHelp')
        if not help_id:
            return redirect('main')

        # Получаем заявку с фиксированным id=1
        help_instance = get_object_or_404(Help, pk=help_id)
        lesion = Lesion.objects.filter(id=1).first()

        # Если заявки нет, создаем её
        if not lesion:
            lesion = Lesion.objects.create(
                id=1,
                client=request.user,
                name="Основная заявка",
                status='draft',
                date_applied=timezone.now()
            )

        # Добавляем связь, если её ещё нет
        if not HelpLesion.objects.filter(help=help_instance, lesion=lesion).exists():
            HelpLesion.objects.create(help=help_instance, lesion=lesion)

    return redirect('main')


def remove_draft_lesion(request):
    if request.method == 'POST':
        print(f"POST данные: {request.POST}")
        remove_lesion = request.POST.get('lesion_id')
        print(f"Переданный ID: {remove_lesion}")

        # Обновляем статус заявки с фиксированным id=1
        with connection.cursor() as cursor:
            cursor.execute(
                'UPDATE main_lesion SET status = CASE WHEN status = %s THEN %s ELSE %s END WHERE id = %s',
                ['draft', 'deleted', 'draft', 1]
            )
        print("Статус заявки переключён")

    return redirect('main')


def get_appl(request):
    # Получаем заявку с фиксированным id=1
    lesion = Lesion.objects.filter(id=1).first()

    # Если заявки нет, создаем её
    if not lesion:
        lesion = Lesion.objects.create(
            id=1,
            client=request.user,
            name="Основная заявка",
            status='draft',
            date_applied=timezone.now()
        )

    relations = HelpLesion.objects.select_related('help', 'lesion').filter(lesion=lesion)
    matched_helps = []

    for relation in relations:
        matched_help = {
            'id': relation.help.id,
            'name': relation.help.name,
            'image': relation.help.image,
            'title': relation.help.title,
            'description': relation.help.description,
            'time': relation.time,
            'comment': relation.comment,
        }
        matched_helps.append(matched_help)

    context = {
        'lesions': lesion,
        'lesion_id': lesion.id,  # ID заявки
        'helps': matched_helps,
    }
    return render(request, 'application.html', context)



from django.shortcuts import render
from datetime import date

data = {'orders': [
            { 'id': 1, 'src_road': 'http://localhost:9000/miniolab1/image/1.png','htitle': 'Сердечно-легочная реанимация', 'title': 'Иногда проведение сердечно-легочной реанимации позволяет спасти жизнь человеку, пока едет скорая помощь. Обсудим основные правила проведения СЛР, какие ошибки чаще всего совершают неподготовленные люди и к чему они могут привести','ht':'Как делать сердечно-легочную реанимацию',
             'description': 'Каждый день в мире сотни человек умирают от внезапной остановки сердца. Настоящими счастливчиками можно считать тех, с кем рядом оказался человек, владеющий навыками базовой сердечно-легочной реанимации (СЛР). Алгоритм СЛР, который предложил в середине ХХ века австрийский анестезиолог Петер Сафар, включал искусственное дыхание «рот в рот» и непрямой массаж сердца. Современные протоколы СЛР рекомендуют сконцентрировать усилия на массаже сердца.'},
            { 'id': 2, 'src_road': 'http://localhost:9000/miniolab1/image/2.png','htitle': 'Искусственное дыхание', 'title': 'Бывают ситуации, когда для спасения человеческой жизни счет идет на минуты. Вместе с врачом скорой помощи обсудим, как правильно провести сердечно-легочную реанимацию и выполнить искусственное дыхание.','ht':'Как делать искусственное дыхание', 'description': '''Искусственное дыхание — это важная процедура, которая может помочь спасти жизнь в экстренной ситуации. 
1. Убедись в безопасности: Проверь, что место безопасно для оказания помощи. 
2. Проверь реакцию пострадавшего: Потряси его за плечи и спрашивай, слышит ли он тебя.
3. Вызови скорую помощь: Если пострадавший не реагирует, позвони в скорую.
4. Освободи дыхательные пути: Положи пострадавшего на спину, запрокинь его голову, подняв подбородок.
5. Проверь дыхание: Посмотри, прислушайся и ощути движение воздуха на щеке в течение 10 секунд.
6. Начни искусственное дыхание:
    - Закрой нос пострадавшего.
    - Плотно обхвати его губы своими и сделай два спокойных выдоха, чтобы грудная клетка слегка поднялась.
    - Каждый вдох должен длиться около 1 секунды.
7. Переходи к массажу сердца, если нужно: В сочетании с искусственным дыханием применяют непрямой массаж сердца (30 надавливаний на грудную клетку и 2 вдоха).
Примечание: Если ты не обучен или не уверен в своих действиях, лучше сосредоточиться на непрямом массаже сердца и вызвать специалистов.'''},
            {'id': 3, 'src_road': 'http://localhost:9000/miniolab1/image/3.png','htitle': 'Наступил на гвоздь', 'title': 'Многие не видят никакой опасности в том, если наступили на гвоздь. Обсудим с врачом, какие осложнения могут быть у такой раны и как оказать первую помощь.',  'ht':'Наступил на ржавый гвоздь', 'description':'''Если человек наступил на ржавый гвоздь, то прежде всего нужно оценить масштаб повреждения. Даже если на первый взгляд кажется, что ранка небольшая, впоследствии нога может распухнуть, покраснеть и причинять сильную боль и дискомфорт со всеми вытекающими отсюда последствиями.
Помимо ржавых гвоздей, люди часто наступают на гвозди, арматуру, проволоку и битое стекло – и каждое подобное повреждение (а уж тем более рана) не должно оставаться без лечения и внимательного (лучше всего медицинского) наблюдения.'''},
            {'id': 4, 'src_road': 'http://localhost:9000/miniolab1/image/4.png','htitle': 'Человек подавился и задыхается', 'title': 'Подавиться может каждый, поэтому очень важно уметь оказать первую помощь в данной ситуации. Составили пошаговую инструкцию, как действовать, а что делать категорически запрещено.', 'ht':'', 'description':''},
            {'id': 5, 'src_road': 'http://localhost:9000/miniolab1/image/5.png','htitle': 'Первая помощь при инсульте', 'title': 'Жизнь и вероятность тяжелых последствий при инсульте напрямую зависят от того, как быстро и грамотно человеку была оказана первая помощь. Поговорим, что можно делать с человеком при инсульте, а что категорически запрещено.', 'ht':'Что делать, если человек подавился и задыхается', 'description':'''Похлопывания по спине:
   - Встаньте сбоку и немного позади человека.
   - Наклоните его вперед.
   - Сделайте до 5 энергичных ударов основанием ладони по спине между лопатками.
Техника Геймлиха (для взрослых и детей старше 1 года):
   - Встаньте позади пострадавшего.
   - Обхватите его руками в области живота, между пупком и нижним краем рёбер.
   - Быстро и сильно сожмите его диафрагму внутрь и вверх.
   - Повторите до 5 раз, если необходимо.'''}, 
]}


def GetOrders(request):
    return render(request, 'orders.html', data)


def GetOrder(request, id):
    order = None
    for current_order in data['orders']:
        if current_order['id'] == id:
            order=current_order
            break
    return render(request, 'order.html', order)




def sendText(request):
    input_text = request.POST['text']
    order = None
    for current_text in data['orders']:
        if input_text == current_text['htitle']:
            order = current_text
            break
    context = {
        'input_text': input_text,
        'order': order
    }
    return render(request, 'search.html', context)


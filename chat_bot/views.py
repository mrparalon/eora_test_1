from django.http import JsonResponse
from django.core import exceptions
from translate.translater import RussianTranslater
from chat_bot.models import BotNode, User, Answer, MessageHistory


def collect_message_history(user, position, message):
    message_history_obj = MessageHistory.objects.create(user=user,
                                                        position=position,
                                                        message=message)
    return message_history_obj


def get_history(request):
    history = MessageHistory.objects.all()
    history_list = []
    for history_obj in history:
        str_to_show = f'User #{history_obj.user.id} {history_obj.time}: {history_obj.message}'
        history_list.append(str_to_show)
    return JsonResponse({'history': history_list})


def get_answer(request):
    if request.method == 'GET':
        message = request.GET.get('message')
        user_id = request.GET.get('user_id')
        if not user_id:
            return JsonResponse({'error': 'Нет user_id'})
        if not message:
            return JsonResponse({'error': 'Введите ответ на вопрос. Введите /start, чтобы вернуться в начало'})

        user = User.objects.get(id=user_id)
        if not user.position and message != '/start':
            return JsonResponse({'error': 'Введите /start для начала'})
        collect_message_history(user, user.position, message)

        if message == '/start':
            start_node = BotNode.objects.get(is_start=True)
            value = start_node.value
            user.position = start_node
            user.save()
            response = {'value': value}
        else:
            message = RussianTranslater(message).translate()
            position = user.position
            try:
                answer_id = Answer.objects.get(answer=message).id
                next_node = position.all_childs.get(answer=answer_id).child
                value = next_node.value
                user.position = next_node
                user.save()
                response = {'value': value}
            except exceptions.ObjectDoesNotExist:
                response = {'error': 'Неправильный ответ',
                            'value': position.value}
        return JsonResponse(response)

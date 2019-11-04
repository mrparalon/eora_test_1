from django.test import TestCase
from django.urls import reverse
from chat_bot.models import Answer, BotNode, ChildParent, MessageHistory, User
from translate.translater import RussianTranslater
import json
# from django.utils.http import urlencode


class QuestionApiTest(TestCase):
    def setUp(self):
        self.user = User.objects.create()
        root_node = BotNode.objects.create(value='root', is_start=True)
        root_yes_node = BotNode.objects.create(value='root_yes')
        root_no_node = BotNode.objects.create(value='root_no')
        root_yes_yes_node = BotNode.objects.create(value='root_yes_yes')
        root_yes_no_node = BotNode.objects.create(value='root_yes_no')
        answer_yes = Answer.objects.create(answer='yes')
        answer_no = Answer.objects.create(answer='no')
        ChildParent.objects.create(parent=root_node,
                                   child=root_yes_node,
                                   answer=answer_yes)
        ChildParent.objects.create(parent=root_node,
                                   child=root_no_node,
                                   answer=answer_no)
        ChildParent.objects.create(parent=root_yes_node,
                                   child=root_yes_yes_node,
                                   answer=answer_yes)
        ChildParent.objects.create(parent=root_yes_node,
                                   child=root_yes_no_node,
                                   answer=answer_no)

    def get_position(self):
        return User.objects.get(id=self.user.id).position

    def test_start(self):
        response_no_position = self.client.get(reverse('chat_bot:get-answer'),
                                               data={'message': 'да'})
        response_start = self.client.get(reverse('chat_bot:get-answer'),
                                         data={'message': '/start',
                                               'user_id': self.user.id})
        response_no_id = self.client.get(reverse('chat_bot:get-answer'),
                                         data={'message': '/start'})
        response_no_message = self.client.get(reverse('chat_bot:get-answer'),
                                              data={'user_id': self.user.id})
        self.assertContains(response_no_position, 'error')
        self.assertContains(response_start, 'root')
        self.assertContains(response_no_id, 'error')
        self.assertContains(response_no_message, 'error')
        self.assertIsNotNone(self.get_position())

    def test_no_user_id(self):
        self.client.get(reverse('chat_bot:get-answer'),
                        data={'message': '/start',
                              'user_id': self.user.id})
        response_yes_no_id = self.client.get(reverse('chat_bot:get-answer'),
                                             data={'message': 'ага'})
        self.assertContains(response_yes_no_id, 'error')

    def test_no_message(self):
        self.client.get(reverse('chat_bot:get-answer'),
                        data={'message': '/start',
                              'user_id': self.user.id})
        response_no_message = self.client.get(reverse('chat_bot:get-answer'),
                                              data={'user_id': self.user.id})
        self.assertContains(response_no_message, 'error')

    def test_tranlater(self):
        YES_LIST = ['да', 'ага', 'йес']
        NO_LIST = ['нет', 'неа', 'ноуп']
        for answer in YES_LIST:
            translated = RussianTranslater(answer).translate()
            self.assertEqual(translated, 'yes')
        for answer in NO_LIST:
            translated = RussianTranslater(answer).translate()
            self.assertEqual(translated, 'no')

    def test_write_answer(self):
        self.client.get(reverse('chat_bot:get-answer'),
                        data={'message': '/start',
                              'user_id': self.user.id})
        response = self.client.get(reverse('chat_bot:get-answer'),
                                   data={'message': 'ага',
                                         'user_id': self.user.id})
        self.assertContains(response, 'root_yes')
        self.assertEqual(self.get_position().value, 'root_yes')
        response = self.client.get(reverse('chat_bot:get-answer'),
                                   data={'message': 'нет',
                                         'user_id': self.user.id})
        self.assertContains(response, 'root_yes_no')
        self.assertEqual(self.get_position().value, 'root_yes_no')

    def test_wrong_answer(self):
        self.client.get(reverse('chat_bot:get-answer'),
                        data={'message': '/start',
                              'user_id': self.user.id})
        response = self.client.get(reverse('chat_bot:get-answer'),
                                   data={'message': 'вероятно',
                                         'user_id': self.user.id})
        self.assertContains(response, 'error')


class MessageHistoryTest(TestCase):
    def setUp(self):
        self.user = User.objects.create()
        root_node = BotNode.objects.create(value='root', is_start=True)
        root_yes_node = BotNode.objects.create(value='root_yes')
        root_no_node = BotNode.objects.create(value='root_no')
        answer_yes = Answer.objects.create(answer='yes')
        answer_no = Answer.objects.create(answer='no')
        ChildParent.objects.create(parent=root_node,
                                   child=root_yes_node,
                                   answer=answer_yes)
        ChildParent.objects.create(parent=root_node,
                                   child=root_no_node,
                                   answer=answer_no)
        self.client.get(reverse('chat_bot:get-answer'),
                        data={'message': '/start',
                              'user_id': self.user.id})
        self.client.get(reverse('chat_bot:get-answer'),
                        data={'message': 'ага',
                              'user_id': self.user.id})

    def test_write_history(self):
        history = MessageHistory.objects.all()
        self.assertIsNotNone(history)
        self.assertEqual(len(history), 2)
        self.assertEqual(history[0].user.id, self.user.id)
        self.assertEqual(history[0].message, '/start')
        self.assertIsNone(history[0].position)
        self.assertIsNotNone(history[0].time)
        self.assertEqual(history[1].user.id, self.user.id)
        self.assertEqual(history[1].message, 'ага')
        self.assertEqual(history[1].position.value, 'root')
        self.assertIsNotNone(history[0].time)

    def test_get_history(self):
        response = self.client.get(reverse('chat_bot:get-history'))
        response_content = response.content.decode('unicode-escape')
        response_content_dict = json.loads(response_content)
        self.assertContains(response, '/start')
        self.assertContains(response, 'ага'.encode('unicode-escape'))
        self.assertContains(response, f'User #{self.user.id}')
        self.assertTrue(isinstance(response_content_dict['history'], list))

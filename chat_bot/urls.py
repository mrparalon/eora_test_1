from django.urls import path
from chat_bot.views import get_answer, get_history

app_name = 'chat_bot'

urlpatterns = [
    path('ask', get_answer, name='get-answer'),
    path('history/', get_history, name='get-history')
]

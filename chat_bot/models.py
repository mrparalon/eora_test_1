from django.db import models


class User(models.Model):
    position = models.ForeignKey('BotNode', on_delete=models.CASCADE,
                                 blank=True, null=True)

    def __str__(self):
        return str(self.id)


class BotNode(models.Model):
    value = models.CharField(max_length=256)
    childs = models.ManyToManyField('BotNode',
                                    through='ChildParent')
    is_start = models.BooleanField(default=False)

    def __str__(self):
        return self.value


class ChildParent(models.Model):
    child = models.ForeignKey('BotNode', on_delete=models.CASCADE,
                              related_name='all_parents')
    parent = models.ForeignKey('BotNode', on_delete=models.CASCADE,
                               related_name='all_childs')
    answer = models.ForeignKey('Answer', on_delete=models.CASCADE)


class Answer(models.Model):
    answer = models.CharField(max_length=32)

    def __str__(self):
        return self.answer


class MessageHistory(models.Model):
    user = models.ForeignKey('User', on_delete=models.CASCADE)
    position = models.ForeignKey('BotNode', on_delete=models.CASCADE,
                                 blank=True, null=True)
    message = models.CharField(max_length=32)
    time = models.DateTimeField(auto_now=True)

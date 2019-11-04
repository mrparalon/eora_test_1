from django.contrib import admin
from chat_bot.models import BotNode, Answer, ChildParent, User


class AnswerAdmin(admin.ModelAdmin):
    pass


class ChildParentInline(admin.TabularInline):
    model = ChildParent
    fk_name = 'child'


class BotNodeAdmin(admin.ModelAdmin):
    inlines = [ChildParentInline]


class UserAdmin(admin.ModelAdmin):
    pass


admin.site.register(BotNode, BotNodeAdmin)
admin.site.register(Answer, AnswerAdmin)
admin.site.register(User, UserAdmin)
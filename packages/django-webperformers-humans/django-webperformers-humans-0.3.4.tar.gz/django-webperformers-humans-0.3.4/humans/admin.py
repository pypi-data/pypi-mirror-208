from django.contrib import admin
from humans.models import Human


@admin.register(Human)
class HumanAdmin(admin.ModelAdmin):
    list_display = ('name', 'position', 'isPublished')
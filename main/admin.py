
from django.contrib import admin
from .models import Profile

@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'level', 'manager')
    list_filter = ('level',)
    search_fields = ('user__username',)

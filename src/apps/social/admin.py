from django.contrib import admin
from .models import Comment


@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ['recipe', 'text', 'created_at']
    search_fields = ['recipe__title']
    readonly_fields = ['created_at']

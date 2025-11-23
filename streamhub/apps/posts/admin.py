from django.contrib import admin
from apps.posts.models import Post


@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    list_display = ['id', 'title', 'author', 'community', 'created_at', 'views_count', 'is_published']
    list_filter = ['is_published', 'created_at', 'community']
    search_fields = ['title', 'content', 'author__username']
    readonly_fields = ['created_at', 'updated_at', 'views_count']
    date_hierarchy = 'created_at'
    ordering = ['-created_at']
    
    fieldsets = (
        ('Основная информация', {
            'fields': ('title', 'content', 'author', 'community')
        }),
        ('Медиа', {
            'fields': ('image',)
        }),
        ('Статус', {
            'fields': ('is_published', 'views_count')
        }),
        ('Временные метки', {
            'fields': ('created_at', 'updated_at')
        }),
    )

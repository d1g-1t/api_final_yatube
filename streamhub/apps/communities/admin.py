from django.contrib import admin
from apps.communities.models import Community


@admin.register(Community)
class CommunityAdmin(admin.ModelAdmin):
    list_display = ['id', 'title', 'slug', 'creator', 'created_at', 'is_active']
    list_filter = ['is_active', 'created_at']
    search_fields = ['title', 'description']
    prepopulated_fields = {'slug': ('title',)}
    readonly_fields = ['created_at']
    date_hierarchy = 'created_at'
    ordering = ['title']
    
    fieldsets = (
        ('Основная информация', {
            'fields': ('title', 'slug', 'description', 'creator')
        }),
        ('Медиа', {
            'fields': ('image',)
        }),
        ('Статус', {
            'fields': ('is_active',)
        }),
        ('Временные метки', {
            'fields': ('created_at',)
        }),
    )

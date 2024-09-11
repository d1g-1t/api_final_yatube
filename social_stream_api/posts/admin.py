from django.contrib import admin
from posts.models import Post, Group, Comment, Follow


class PostAdmin(admin.ModelAdmin):
    """
    Админ-класс для модели Post.
    Определяет отображение и поведение постов в админ-панели.
    """
    list_display = ('pk', 'text', 'pub_date', 'author', 'group')
    search_fields = ('text',)
    list_filter = ('pub_date',)
    list_editable = ('group',)
    search_fields = ('text',)
    empty_value_display = '-пусто'


class GroupAdmin(admin.ModelAdmin):
    """
    Админ-класс для модели Group.
    Определяет отображение и поведение групп в админ-панели.
    """
    list_display = ('pk', 'title', 'slug', 'description')


class CommentAdmin(admin.ModelAdmin):
    """
    Админ-класс для модели Comment.
    Определяет отображение и поведение комментариев в админ-панели.
    """
    list_display = ('post', 'author', 'text', 'created')


class FollowAdmin(admin.ModelAdmin):
    """
    Админ-класс для модели Follow.
    Определяет отображение и поведение подписок в админ-панели.
    """
    list_display = ('user', 'following')


admin.site.register(Post, PostAdmin)
admin.site.register(Group, GroupAdmin)
admin.site.register(Comment, CommentAdmin)
admin.site.register(Follow, FollowAdmin)

"""
Модели для работы с постами и сообществами.
Реализуют Service Layer Pattern и оптимизированы для производительности.
"""
from django.contrib.auth import get_user_model
from django.core.validators import MinLengthValidator, FileExtensionValidator
from django.db import models
from django.db.models import Q, F
from django.utils.text import slugify
from django.utils.translation import gettext_lazy as _

from common.models import BaseModel

User = get_user_model()


class CommunityQuerySet(models.QuerySet):
    """Кастомный QuerySet для оптимизированных запросов сообществ"""
    
    def active(self):
        """Только активные (не удаленные) сообщества"""
        return self.filter(is_deleted=False)
    
    def with_posts_count(self):
        """Добавляет количество постов"""
        return self.annotate(
            total_posts=models.Count('posts', filter=Q(posts__is_published=True, posts__is_deleted=False))
        )
    
    def popular(self, limit=10):
        """Популярные сообщества по количеству постов"""
        return self.with_posts_count().order_by('-total_posts')[:limit]


class CommunityManager(models.Manager):
    """Менеджер для работы с сообществами"""
    
    def get_queryset(self):
        return CommunityQuerySet(self.model, using=self._db)
    
    def active(self):
        return self.get_queryset().active()
    
    def with_posts_count(self):
        return self.get_queryset().with_posts_count()


class Community(BaseModel):
    """
    Модель сообщества (группы).
    
    Сообщество - это тематическое объединение постов.
    Оптимизировано для быстрого поиска и агрегации данных.
    """
    title = models.CharField(
        max_length=200,
        validators=[MinLengthValidator(3)],
        verbose_name=_("Название"),
        help_text=_("Название сообщества (3-200 символов)")
    )
    slug = models.SlugField(
        max_length=200,
        unique=True,
        db_index=True,
        verbose_name=_("URL идентификатор"),
        help_text=_("Уникальный идентификатор для URL")
    )
    description = models.TextField(
        validators=[MinLengthValidator(10)],
        verbose_name=_("Описание"),
        help_text=_("Подробное описание сообщества")
    )
    avatar = models.ImageField(
        upload_to='communities/avatars/%Y/%m/',
        null=True,
        blank=True,
        validators=[
            FileExtensionValidator(allowed_extensions=['jpg', 'jpeg', 'png', 'webp'])
        ],
        verbose_name=_("Аватар сообщества")
    )
    is_private = models.BooleanField(
        default=False,
        db_index=True,
        verbose_name=_("Приватное сообщество")
    )
    
    objects = CommunityManager()
    
    class Meta:
        verbose_name = _("Сообщество")
        verbose_name_plural = _("Сообщества")
        ordering = ['title']
        indexes = [
            models.Index(fields=['slug']),
            models.Index(fields=['is_private', '-created_at']),
            models.Index(fields=['-created_at'], name='community_created_idx'),
        ]
        constraints = [
            models.CheckConstraint(
                check=models.Q(title__regex=r'.{3,}'),
                name='community_title_min_length'
            ),
        ]

    def __str__(self):
        return self.title
    
    def save(self, *args, **kwargs):
        """Автоматическая генерация slug при создании"""
        if not self.slug:
            self.slug = slugify(self.title)
        super().save(*args, **kwargs)


class PostQuerySet(models.QuerySet):
    """Кастомный QuerySet для оптимизированных запросов постов"""
    
    def active(self):
        """Только активные (не удаленные) посты"""
        return self.filter(is_deleted=False)
    
    def published(self):
        """Только опубликованные посты"""
        return self.filter(is_published=True, is_deleted=False)
    
    def with_author_and_community(self):
        """Оптимизация: загружает автора и сообщество за один запрос"""
        return self.select_related('author', 'community')
    
    def with_comments_count(self):
        """Добавляет количество комментариев"""
        return self.annotate(
            comments_count=models.Count('comments', filter=Q(comments__is_deleted=False))
        )
    
    def with_full_data(self):
        """Полная оптимизация для списка постов"""
        return (
            self.published()
            .with_author_and_community()
            .with_comments_count()
            .prefetch_related('comments__author')
        )
    
    def by_author(self, author):
        """Посты конкретного автора"""
        return self.filter(author=author)
    
    def by_community(self, community_slug):
        """Посты конкретного сообщества"""
        return self.filter(community__slug=community_slug)
    
    def search(self, query):
        """Полнотекстовый поиск по заголовку и содержимому"""
        return self.filter(
            Q(title__icontains=query) | Q(content__icontains=query)
        )
    
    def trending(self, days=7):
        """Трендовые посты за последние N дней"""
        from django.utils import timezone
        from datetime import timedelta
        
        date_from = timezone.now() - timedelta(days=days)
        return self.filter(created_at__gte=date_from).order_by('-views_count', '-created_at')


class PostManager(models.Manager):
    """Менеджер для работы с постами"""
    
    def get_queryset(self):
        return PostQuerySet(self.model, using=self._db)
    
    def published(self):
        return self.get_queryset().published()
    
    def with_full_data(self):
        return self.get_queryset().with_full_data()


class Post(BaseModel):
    """
    Модель поста.
    
    Пост - основная единица контента в системе.
    Оптимизирован для быстрой загрузки и поиска.
    """
    title = models.CharField(
        max_length=300,
        validators=[MinLengthValidator(5)],
        db_index=True,
        verbose_name=_("Заголовок"),
        help_text=_("Заголовок поста (5-300 символов)")
    )
    content = models.TextField(
        validators=[MinLengthValidator(10)],
        verbose_name=_("Содержание"),
        help_text=_("Основной текст поста")
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='posts',
        db_index=True,
        verbose_name=_("Автор")
    )
    community = models.ForeignKey(
        Community,
        on_delete=models.SET_NULL,
        related_name='posts',
        null=True,
        blank=True,
        db_index=True,
        verbose_name=_("Сообщество")
    )
    image = models.ImageField(
        upload_to='posts/images/%Y/%m/%d/',
        null=True,
        blank=True,
        validators=[
            FileExtensionValidator(allowed_extensions=['jpg', 'jpeg', 'png', 'webp'])
        ],
        verbose_name=_("Изображение")
    )
    is_published = models.BooleanField(
        default=True,
        db_index=True,
        verbose_name=_("Опубликован")
    )
    views_count = models.PositiveIntegerField(
        default=0,
        db_index=True,
        verbose_name=_("Количество просмотров")
    )
    is_pinned = models.BooleanField(
        default=False,
        db_index=True,
        verbose_name=_("Закреплен"),
        help_text=_("Закрепленные посты отображаются в начале списка")
    )
    
    objects = PostManager()
    
    class Meta:
        verbose_name = _("Пост")
        verbose_name_plural = _("Посты")
        ordering = ['-is_pinned', '-created_at']
        indexes = [
            models.Index(fields=['-created_at', 'author'], name='post_created_author_idx'),
            models.Index(fields=['community', '-created_at'], name='post_community_created_idx'),
            models.Index(fields=['-views_count'], name='post_views_idx'),
            models.Index(fields=['is_published', '-created_at'], name='post_published_idx'),
            models.Index(fields=['is_pinned', '-created_at'], name='post_pinned_idx'),
        ]
        constraints = [
            models.CheckConstraint(
                check=models.Q(title__regex=r'.{5,}'),
                name='post_title_min_length'
            ),
            models.CheckConstraint(
                check=models.Q(views_count__gte=0),
                name='post_views_positive'
            ),
        ]

    def __str__(self):
        return self.title[:100]
    
    def increment_views(self):
        """Безопасный инкремент просмотров без race condition"""
        Post.objects.filter(pk=self.pk).update(views_count=F('views_count') + 1)

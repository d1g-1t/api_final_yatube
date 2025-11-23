"""
Модели для взаимодействий пользователей.
Включает комментарии, подписки, лайки и другие социальные функции.
"""
from django.contrib.auth import get_user_model
from django.core.validators import MinLengthValidator
from django.db import models
from django.db.models import Q
from django.utils.translation import gettext_lazy as _

from apps.posts.models import Post
from common.models import BaseModel

User = get_user_model()


class CommentQuerySet(models.QuerySet):
    """Кастомный QuerySet для комментариев"""
    
    def active(self):
        """Только активные комментарии"""
        return self.filter(is_deleted=False)
    
    def for_post(self, post_id):
        """Комментарии для конкретного поста"""
        return self.filter(post_id=post_id)
    
    def with_author(self):
        """Оптимизация: загружает автора"""
        return self.select_related('author', 'post')
    
    def root_comments(self):
        """Только корневые комментарии (не ответы)"""
        return self.filter(parent__isnull=True)
    
    def replies(self):
        """Только ответы на комментарии"""
        return self.filter(parent__isnull=False)


class CommentManager(models.Manager):
    """Менеджер для комментариев"""
    
    def get_queryset(self):
        return CommentQuerySet(self.model, using=self._db)
    
    def active(self):
        return self.get_queryset().active()


class Comment(BaseModel):
    """
    Модель комментария к посту.
    
    Поддерживает вложенные комментарии (ответы).
    Оптимизирован для иерархической структуры.
    """
    post = models.ForeignKey(
        Post,
        on_delete=models.CASCADE,
        related_name='comments',
        db_index=True,
        verbose_name=_("Пост")
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='comments',
        db_index=True,
        verbose_name=_("Автор")
    )
    parent = models.ForeignKey(
        'self',
        on_delete=models.CASCADE,
        related_name='replies',
        null=True,
        blank=True,
        verbose_name=_("Родительский комментарий"),
        help_text=_("Оставьте пустым для корневого комментария")
    )
    content = models.TextField(
        validators=[MinLengthValidator(1)],
        verbose_name=_("Текст комментария"),
        help_text=_("Содержание комментария")
    )
    is_edited = models.BooleanField(
        default=False,
        verbose_name=_("Отредактирован")
    )
    
    objects = CommentManager()
    
    class Meta:
        verbose_name = _("Комментарий")
        verbose_name_plural = _("Комментарии")
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['post', '-created_at'], name='comment_post_created_idx'),
            models.Index(fields=['author', '-created_at'], name='comment_author_created_idx'),
            models.Index(fields=['parent', '-created_at'], name='comment_parent_idx'),
        ]
    
    def __str__(self):
        return f'{self.author.username}: {self.content[:50]}'
    
    def save(self, *args, **kwargs):
        """Отслеживание редактирования"""
        if self.pk:  # Существующий комментарий
            original = Comment.objects.get(pk=self.pk)
            if original.content != self.content:
                self.is_edited = True
        super().save(*args, **kwargs)


class SubscriptionQuerySet(models.QuerySet):
    """Кастомный QuerySet для подписок"""
    
    def active(self):
        """Активные подписки"""
        return self.filter(is_active=True)
    
    def for_user(self, user):
        """Подписки конкретного пользователя"""
        return self.filter(subscriber=user)
    
    def subscribers_of(self, user):
        """Подписчики конкретного пользователя"""
        return self.filter(target_user=user)


class SubscriptionManager(models.Manager):
    """Менеджер для подписок"""
    
    def get_queryset(self):
        return SubscriptionQuerySet(self.model, using=self._db)
    
    def active(self):
        return self.get_queryset().active()


class Subscription(BaseModel):
    """
    Модель подписки пользователя на другого пользователя.
    
    Реализует систему подписок для создания персонализированной ленты.
    """
    subscriber = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='following',
        db_index=True,
        verbose_name=_("Подписчик")
    )
    target_user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='followers',
        db_index=True,
        verbose_name=_("Цель подписки")
    )
    is_active = models.BooleanField(
        default=True,
        db_index=True,
        verbose_name=_("Активна")
    )
    
    objects = SubscriptionManager()
    
    class Meta:
        verbose_name = _("Подписка")
        verbose_name_plural = _("Подписки")
        ordering = ['-created_at']
        unique_together = [['subscriber', 'target_user']]
        indexes = [
            models.Index(fields=['subscriber', 'is_active'], name='subscription_subscriber_idx'),
            models.Index(fields=['target_user', 'is_active'], name='subscription_target_idx'),
            models.Index(fields=['-created_at'], name='subscription_created_idx'),
        ]
        constraints = [
            models.CheckConstraint(
                check=~Q(subscriber=models.F('target_user')),
                name='cannot_subscribe_to_self'
            ),
        ]
    
    def __str__(self):
        return f'{self.subscriber.username} → {self.target_user.username}'


class LikeQuerySet(models.QuerySet):
    """Кастомный QuerySet для лайков"""
    
    def for_post(self, post):
        """Лайки конкретного поста"""
        return self.filter(post=post)
    
    def by_user(self, user):
        """Лайки конкретного пользователя"""
        return self.filter(user=user)


class LikeManager(models.Manager):
    """Менеджер для лайков"""
    
    def get_queryset(self):
        return LikeQuerySet(self.model, using=self._db)


class Like(BaseModel):
    """
    Модель лайка к посту.
    
    Простая система реакций на посты.
    """
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='likes',
        db_index=True,
        verbose_name=_("Пользователь")
    )
    post = models.ForeignKey(
        Post,
        on_delete=models.CASCADE,
        related_name='likes',
        db_index=True,
        verbose_name=_("Пост")
    )
    
    objects = LikeManager()
    
    class Meta:
        verbose_name = _("Лайк")
        verbose_name_plural = _("Лайки")
        ordering = ['-created_at']
        unique_together = [['user', 'post']]
        indexes = [
            models.Index(fields=['post', '-created_at'], name='like_post_idx'),
            models.Index(fields=['user', '-created_at'], name='like_user_idx'),
        ]
    
    def __str__(self):
        return f'{self.user.username} ❤️ {self.post.title[:30]}'

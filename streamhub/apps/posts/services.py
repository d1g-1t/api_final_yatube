"""
Service Layer для работы с постами и сообществами.
Инкапсулирует бизнес-логику и обеспечивает транзакционную целостность.
"""
from typing import Optional, Dict, Any
from django.contrib.auth import get_user_model
from django.db import transaction
from django.db.models import F
from django.core.exceptions import ValidationError
from django.utils.text import slugify

from .models import Post, Community
from common.cache import invalidate_cache_pattern
import logging

User = get_user_model()
logger = logging.getLogger(__name__)


class PostService:
    """
    Сервис для управления постами.
    
    Реализует все операции создания, обновления и удаления постов
    с соблюдением бизнес-правил и транзакционной целостности.
    """
    
    @staticmethod
    @transaction.atomic
    def create_post(
        author: User,
        title: str,
        content: str,
        community: Optional[Community] = None,
        image: Optional[Any] = None,
        is_published: bool = True
    ) -> Post:
        """
        Создает новый пост.
        
        Args:
            author: Автор поста
            title: Заголовок поста
            content: Содержание поста
            community: Сообщество (опционально)
            image: Изображение (опционально)
            is_published: Опубликован ли пост
            
        Returns:
            Post: Созданный пост
            
        Raises:
            ValidationError: Если данные невалидны
        """
        # Валидация
        if len(title) < 5:
            raise ValidationError("Заголовок должен содержать минимум 5 символов")
        
        if len(content) < 10:
            raise ValidationError("Содержание должно содержать минимум 10 символов")
        
        # Создание поста
        post = Post.objects.create(
            author=author,
            title=title.strip(),
            content=content.strip(),
            community=community,
            image=image,
            is_published=is_published
        )
        
        # Инвалидация кэша
        invalidate_cache_pattern('post_list')
        if community:
            invalidate_cache_pattern(f'community_{community.slug}_posts')
        
        logger.info(
            f"Создан пост ID:{post.id} '{post.title}' пользователем {author.username}",
            extra={'post_id': post.id, 'author_id': author.id}
        )
        
        return post
    
    @staticmethod
    @transaction.atomic
    def update_post(
        post: Post,
        title: Optional[str] = None,
        content: Optional[str] = None,
        community: Optional[Community] = None,
        image: Optional[Any] = None,
        is_published: Optional[bool] = None
    ) -> Post:
        """
        Обновляет существующий пост.
        
        Args:
            post: Пост для обновления
            title: Новый заголовок (опционально)
            content: Новое содержание (опционально)
            community: Новое сообщество (опционально)
            image: Новое изображение (опционально)
            is_published: Новый статус публикации (опционально)
            
        Returns:
            Post: Обновленный пост
        """
        update_fields = ['updated_at']
        
        if title is not None:
            if len(title) < 5:
                raise ValidationError("Заголовок должен содержать минимум 5 символов")
            post.title = title.strip()
            update_fields.append('title')
        
        if content is not None:
            if len(content) < 10:
                raise ValidationError("Содержание должно содержать минимум 10 символов")
            post.content = content.strip()
            update_fields.append('content')
        
        if community is not None:
            post.community = community
            update_fields.append('community')
        
        if image is not None:
            post.image = image
            update_fields.append('image')
        
        if is_published is not None:
            post.is_published = is_published
            update_fields.append('is_published')
        
        post.save(update_fields=update_fields)
        
        # Инвалидация кэша
        invalidate_cache_pattern('post_list')
        invalidate_cache_pattern(f'post_{post.id}')
        if post.community:
            invalidate_cache_pattern(f'community_{post.community.slug}_posts')
        
        logger.info(
            f"Обновлен пост ID:{post.id}",
            extra={'post_id': post.id, 'updated_fields': update_fields}
        )
        
        return post
    
    @staticmethod
    def increment_views(post: Post) -> Post:
        """
        Увеличивает счетчик просмотров поста.
        Использует F-выражение для предотвращения race conditions.
        
        Args:
            post: Пост для обновления
            
        Returns:
            Post: Пост с обновленным счетчиком
        """
        Post.objects.filter(pk=post.pk).update(views_count=F('views_count') + 1)
        post.refresh_from_db(fields=['views_count'])
        
        logger.debug(f"Просмотр поста ID:{post.id}, всего просмотров: {post.views_count}")
        
        return post
    
    @staticmethod
    @transaction.atomic
    def delete_post(post: Post, hard_delete: bool = False) -> None:
        """
        Удаляет пост (мягкое или жесткое удаление).
        
        Args:
            post: Пост для удаления
            hard_delete: Если True, удаляет физически, иначе - мягкое удаление
        """
        post_id = post.id
        author = post.author.username
        community_slug = post.community.slug if post.community else None
        
        if hard_delete:
            post.delete()
            logger.warning(f"Жесткое удаление поста ID:{post_id} пользователем {author}")
        else:
            post.soft_delete()
            logger.info(f"Мягкое удаление поста ID:{post_id} пользователем {author}")
        
        # Инвалидация кэша
        invalidate_cache_pattern('post_list')
        invalidate_cache_pattern(f'post_{post_id}')
        if community_slug:
            invalidate_cache_pattern(f'community_{community_slug}_posts')
    
    @staticmethod
    @transaction.atomic
    def toggle_pin(post: Post) -> Post:
        """
        Переключает статус закрепления поста.
        
        Args:
            post: Пост для закрепления/открепления
            
        Returns:
            Post: Пост с обновленным статусом
        """
        post.is_pinned = not post.is_pinned
        post.save(update_fields=['is_pinned', 'updated_at'])
        
        action = "закреплен" if post.is_pinned else "откреплен"
        logger.info(f"Пост ID:{post.id} {action}")
        
        # Инвалидация кэша
        invalidate_cache_pattern('post_list')
        if post.community:
            invalidate_cache_pattern(f'community_{post.community.slug}_posts')
        
        return post


class CommunityService:
    """
    Сервис для управления сообществами.
    
    Реализует операции создания, обновления и удаления сообществ.
    """
    
    @staticmethod
    @transaction.atomic
    def create_community(
        title: str,
        description: str,
        slug: Optional[str] = None,
        avatar: Optional[Any] = None,
        is_private: bool = False
    ) -> Community:
        """
        Создает новое сообщество.
        
        Args:
            title: Название сообщества
            description: Описание сообщества
            slug: URL идентификатор (опционально, генерируется автоматически)
            avatar: Аватар сообщества (опционально)
            is_private: Приватное ли сообщество
            
        Returns:
            Community: Созданное сообщество
            
        Raises:
            ValidationError: Если данные невалидны
        """
        # Валидация
        if len(title) < 3:
            raise ValidationError("Название должно содержать минимум 3 символа")
        
        if len(description) < 10:
            raise ValidationError("Описание должно содержать минимум 10 символов")
        
        # Генерация slug если не указан
        if not slug:
            slug = slugify(title)
        
        # Проверка уникальности slug
        if Community.objects.filter(slug=slug).exists():
            raise ValidationError(f"Сообщество с идентификатором '{slug}' уже существует")
        
        # Создание сообщества
        community = Community.objects.create(
            title=title.strip(),
            description=description.strip(),
            slug=slug,
            avatar=avatar,
            is_private=is_private
        )
        
        # Инвалидация кэша
        invalidate_cache_pattern('community_list')
        
        logger.info(
            f"Создано сообщество '{title}' (slug: {slug})",
            extra={'community_id': community.id, 'slug': slug}
        )
        
        return community
    
    @staticmethod
    @transaction.atomic
    def update_community(
        community: Community,
        title: Optional[str] = None,
        description: Optional[str] = None,
        avatar: Optional[Any] = None,
        is_private: Optional[bool] = None
    ) -> Community:
        """
        Обновляет существующее сообщество.
        
        Args:
            community: Сообщество для обновления
            title: Новое название (опционально)
            description: Новое описание (опционально)
            avatar: Новый аватар (опционально)
            is_private: Новый статус приватности (опционально)
            
        Returns:
            Community: Обновленное сообщество
        """
        update_fields = ['updated_at']
        
        if title is not None:
            if len(title) < 3:
                raise ValidationError("Название должно содержать минимум 3 символа")
            community.title = title.strip()
            update_fields.append('title')
        
        if description is not None:
            if len(description) < 10:
                raise ValidationError("Описание должно содержать минимум 10 символов")
            community.description = description.strip()
            update_fields.append('description')
        
        if avatar is not None:
            community.avatar = avatar
            update_fields.append('avatar')
        
        if is_private is not None:
            community.is_private = is_private
            update_fields.append('is_private')
        
        community.save(update_fields=update_fields)
        
        # Инвалидация кэша
        invalidate_cache_pattern('community_list')
        invalidate_cache_pattern(f'community_{community.slug}')
        
        logger.info(
            f"Обновлено сообщество '{community.title}'",
            extra={'community_id': community.id, 'updated_fields': update_fields}
        )
        
        return community
    
    @staticmethod
    @transaction.atomic
    def delete_community(community: Community, hard_delete: bool = False) -> None:
        """
        Удаляет сообщество.
        
        Args:
            community: Сообщество для удаления
            hard_delete: Если True, удаляет физически, иначе - мягкое удаление
        """
        community_id = community.id
        title = community.title
        slug = community.slug
        
        if hard_delete:
            community.delete()
            logger.warning(f"Жесткое удаление сообщества '{title}' (ID:{community_id})")
        else:
            community.soft_delete()
            logger.info(f"Мягкое удаление сообщества '{title}' (ID:{community_id})")
        
        # Инвалидация кэша
        invalidate_cache_pattern('community_list')
        invalidate_cache_pattern(f'community_{slug}')

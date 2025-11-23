"""
Selector Layer для оптимизированных запросов к постам и сообществам.
Инкапсулирует всю логику получения данных с оптимизациями и кэшированием.
"""
from typing import Optional, List
from django.db.models import Count, Prefetch, Q, QuerySet, Exists, OuterRef
from django.contrib.auth import get_user_model
from django.core.cache import cache

from .models import Post, Community
from apps.interactions.models import Comment, Like
from common.cache import cache_result, make_cache_key
import logging

User = get_user_model()
logger = logging.getLogger(__name__)


class PostSelector:
    """
    Селектор для оптимизированного получения постов.
    
    Реализует паттерн Selector для изоляции логики запросов к БД.
    Все методы возвращают оптимизированные QuerySet с необходимыми prefetch и annotate.
    """
    
    @staticmethod
    def get_base_queryset() -> QuerySet[Post]:
        """
        Базовый QuerySet для постов с основными оптимизациями.
        
        Returns:
            QuerySet с оптимизированной загрузкой связанных данных
        """
        return (
            Post.objects
            .published()
            .select_related('author', 'community')
            .prefetch_related(
                Prefetch(
                    'comments',
                    queryset=Comment.objects.active().select_related('author').order_by('-created_at')[:10]
                )
            )
            .annotate(
                comments_count=Count('comments', filter=Q(comments__is_deleted=False)),
                likes_count=Count('likes', filter=Q(likes__is_deleted=False), distinct=True)
            )
        )
    
    @staticmethod
    @cache_result(timeout=300, key_prefix='post_list')
    def get_published_posts() -> QuerySet[Post]:
        """
        Получает список всех опубликованных постов.
        Результат кэшируется на 5 минут.
        
        Returns:
            QuerySet опубликованных постов с оптимизацией
        """
        logger.debug("Получение списка опубликованных постов")
        return PostSelector.get_base_queryset()
    
    @staticmethod
    def get_post_by_id(post_id: int) -> Optional[Post]:
        """
        Получает пост по ID с полной оптимизацией.
        
        Args:
            post_id: ID поста
            
        Returns:
            Пост или None если не найден
        """
        cache_key = make_cache_key('post_detail', post_id)
        post = cache.get(cache_key)
        
        if post is None:
            try:
                post = PostSelector.get_base_queryset().get(pk=post_id)
                cache.set(cache_key, post, 600)  # 10 минут
                logger.debug(f"Получен пост ID:{post_id} из БД и закэширован")
            except Post.DoesNotExist:
                logger.warning(f"Пост с ID {post_id} не найден")
                return None
        else:
            logger.debug(f"Получен пост ID:{post_id} из кэша")
        
        return post
    
    @staticmethod
    def get_posts_by_author(author: User) -> QuerySet[Post]:
        """
        Получает посты конкретного автора.
        
        Args:
            author: Автор постов
            
        Returns:
            QuerySet постов автора
        """
        logger.debug(f"Получение постов автора: {author.username}")
        return PostSelector.get_base_queryset().filter(author=author)
    
    @staticmethod
    @cache_result(timeout=300, key_prefix='community_posts')
    def get_posts_by_community(community_slug: str) -> QuerySet[Post]:
        """
        Получает посты конкретного сообщества.
        Результат кэшируется на 5 минут.
        
        Args:
            community_slug: Slug сообщества
            
        Returns:
            QuerySet постов сообщества
        """
        logger.debug(f"Получение постов сообщества: {community_slug}")
        return PostSelector.get_base_queryset().filter(community__slug=community_slug)
    
    @staticmethod
    def get_user_feed(user: User, limit: int = 50) -> QuerySet[Post]:
        """
        Получает персонализированную ленту пользователя.
        Показывает посты от тех, на кого подписан пользователь.
        
        Args:
            user: Пользователь для которого формируется лента
            limit: Максимальное количество постов
            
        Returns:
            QuerySet постов для ленты пользователя
        """
        logger.debug(f"Получение ленты пользователя: {user.username}")
        
        from apps.interactions.models import Subscription
        
        # Получаем ID пользователей, на которых подписан
        following_ids = Subscription.objects.filter(
            subscriber=user,
            is_active=True
        ).values_list('target_user_id', flat=True)
        
        return (
            PostSelector.get_base_queryset()
            .filter(author_id__in=following_ids)
            .order_by('-is_pinned', '-created_at')[:limit]
        )
    
    @staticmethod
    def search_posts(query: str, limit: int = 100) -> QuerySet[Post]:
        """
        Полнотекстовый поиск постов.
        
        Args:
            query: Поисковый запрос
            limit: Максимальное количество результатов
            
        Returns:
            QuerySet найденных постов
        """
        logger.info(f"Поиск постов по запросу: '{query}'")
        
        return (
            PostSelector.get_base_queryset()
            .filter(Q(title__icontains=query) | Q(content__icontains=query))
            .order_by('-created_at')[:limit]
        )
    
    @staticmethod
    def get_trending_posts(days: int = 7, limit: int = 20) -> QuerySet[Post]:
        """
        Получает трендовые посты за последние N дней.
        
        Args:
            days: Количество дней для анализа
            limit: Максимальное количество постов
            
        Returns:
            QuerySet трендовых постов
        """
        from django.utils import timezone
        from datetime import timedelta
        
        date_from = timezone.now() - timedelta(days=days)
        
        logger.debug(f"Получение трендовых постов за {days} дней")
        
        return (
            PostSelector.get_base_queryset()
            .filter(created_at__gte=date_from)
            .order_by('-views_count', '-likes_count', '-comments_count')[:limit]
        )
    
    @staticmethod
    def get_posts_with_user_context(user: User) -> QuerySet[Post]:
        """
        Получает посты с контекстом пользователя (лайки, закладки).
        
        Args:
            user: Пользователь для контекста
            
        Returns:
            QuerySet с аннотациями о взаимодействиях пользователя
        """
        logger.debug(f"Получение постов с контекстом пользователя: {user.username}")
        
        return (
            PostSelector.get_base_queryset()
            .annotate(
                is_liked_by_user=Exists(
                    Like.objects.filter(
                        post=OuterRef('pk'),
                        user=user,
                        is_deleted=False
                    )
                )
            )
        )


class CommunitySelector:
    """
    Селектор для оптимизированного получения сообществ.
    """
    
    @staticmethod
    def get_base_queryset() -> QuerySet[Community]:
        """
        Базовый QuerySet для сообществ.
        
        Returns:
            QuerySet с базовыми аннотациями
        """
        return (
            Community.objects
            .active()
            .annotate(
                posts_count=Count('posts', filter=Q(posts__is_published=True, posts__is_deleted=False)),
                total_members=Count('posts__author', distinct=True)
            )
        )
    
    @staticmethod
    @cache_result(timeout=600, key_prefix='community_list')
    def get_all_communities() -> QuerySet[Community]:
        """
        Получает все активные сообщества.
        Результат кэшируется на 10 минут.
        
        Returns:
            QuerySet всех сообществ
        """
        logger.debug("Получение списка всех сообществ")
        return CommunitySelector.get_base_queryset().order_by('title')
    
    @staticmethod
    def get_community_by_slug(slug: str) -> Optional[Community]:
        """
        Получает сообщество по slug.
        
        Args:
            slug: URL идентификатор сообщества
            
        Returns:
            Сообщество или None
        """
        cache_key = make_cache_key('community_detail', slug)
        community = cache.get(cache_key)
        
        if community is None:
            try:
                community = CommunitySelector.get_base_queryset().get(slug=slug)
                cache.set(cache_key, community, 600)
                logger.debug(f"Получено сообщество '{slug}' из БД и закэшировано")
            except Community.DoesNotExist:
                logger.warning(f"Сообщество с slug '{slug}' не найдено")
                return None
        else:
            logger.debug(f"Получено сообщество '{slug}' из кэша")
        
        return community
    
    @staticmethod
    def get_popular_communities(limit: int = 10) -> QuerySet[Community]:
        """
        Получает популярные сообщества по количеству постов.
        
        Args:
            limit: Количество сообществ
            
        Returns:
            QuerySet популярных сообществ
        """
        logger.debug(f"Получение топ-{limit} популярных сообществ")
        
        return (
            CommunitySelector.get_base_queryset()
            .filter(is_private=False)
            .order_by('-posts_count', '-total_members')[:limit]
        )
    
    @staticmethod
    def search_communities(query: str) -> QuerySet[Community]:
        """
        Поиск сообществ по названию и описанию.
        
        Args:
            query: Поисковый запрос
            
        Returns:
            QuerySet найденных сообществ
        """
        logger.info(f"Поиск сообществ по запросу: '{query}'")
        
        return (
            CommunitySelector.get_base_queryset()
            .filter(
                Q(title__icontains=query) | Q(description__icontains=query),
                is_private=False
            )
            .order_by('-posts_count')
        )

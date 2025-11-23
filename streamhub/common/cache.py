"""
Утилиты для работы с кэшированием.
Реализует многоуровневое кэширование и инвалидацию по паттернам.
"""
from functools import wraps
from typing import Any, Optional, Callable
from django.core.cache import cache
from django.conf import settings
import hashlib
import json
import logging

logger = logging.getLogger(__name__)


def make_cache_key(prefix: str, *args, **kwargs) -> str:
    """
    Генерирует уникальный ключ кэша на основе префикса и аргументов.
    
    Args:
        prefix: Префикс ключа
        *args: Позиционные аргументы
        **kwargs: Именованные аргументы
        
    Returns:
        str: Хэшированный ключ кэша
    """
    key_data = f"{prefix}:{args}:{sorted(kwargs.items())}"
    return f"{settings.CACHES['default'].get('KEY_PREFIX', 'app')}:{hashlib.md5(key_data.encode()).hexdigest()}"


def cache_result(timeout: int = 300, key_prefix: str = 'cache'):
    """
    Декоратор для кэширования результатов функций.
    
    Args:
        timeout: Время жизни кэша в секундах
        key_prefix: Префикс для ключа кэша
        
    Example:
        @cache_result(timeout=600, key_prefix='user_posts')
        def get_user_posts(user_id):
            return Post.objects.filter(author_id=user_id)
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs):
            cache_key = make_cache_key(key_prefix, *args, **kwargs)
            
            # Попытка получить из кэша
            result = cache.get(cache_key)
            
            if result is None:
                logger.debug(f"Cache MISS for key: {cache_key}")
                result = func(*args, **kwargs)
                
                # Сохранение в кэш
                try:
                    cache.set(cache_key, result, timeout)
                    logger.debug(f"Cache SET for key: {cache_key}, timeout: {timeout}s")
                except Exception as e:
                    logger.error(f"Failed to cache result: {e}")
            else:
                logger.debug(f"Cache HIT for key: {cache_key}")
            
            return result
        return wrapper
    return decorator


def invalidate_cache(key: str) -> None:
    """
    Инвалидирует конкретный ключ кэша.
    
    Args:
        key: Ключ для инвалидации
    """
    try:
        cache.delete(key)
        logger.debug(f"Cache invalidated: {key}")
    except Exception as e:
        logger.error(f"Failed to invalidate cache key {key}: {e}")


def invalidate_cache_pattern(pattern: str) -> int:
    """
    Инвалидирует все ключи кэша, соответствующие паттерну.
    
    Args:
        pattern: Паттерн для поиска ключей
        
    Returns:
        int: Количество инвалидированных ключей
    """
    try:
        # Используем Redis-специфичный функционал
        from django_redis import get_redis_connection
        
        redis_conn = get_redis_connection("default")
        prefix = settings.CACHES['default'].get('KEY_PREFIX', 'app')
        full_pattern = f"{prefix}:*{pattern}*"
        
        keys = redis_conn.keys(full_pattern)
        
        if keys:
            count = redis_conn.delete(*keys)
            logger.info(f"Invalidated {count} cache keys matching pattern: {pattern}")
            return count
        
        logger.debug(f"No cache keys found for pattern: {pattern}")
        return 0
        
    except ImportError:
        # Fallback для не-Redis кэша
        logger.warning("Pattern-based cache invalidation requires Redis backend")
        return 0
    except Exception as e:
        logger.error(f"Failed to invalidate cache pattern {pattern}: {e}")
        return 0


def cache_page_with_user(timeout: int = 300):
    """
    Декоратор для кэширования страниц с учетом пользователя.
    
    Args:
        timeout: Время жизни кэша в секундах
    """
    def decorator(view_func: Callable) -> Callable:
        @wraps(view_func)
        def wrapper(request, *args, **kwargs):
            # Генерация ключа с учетом пользователя
            user_id = request.user.id if request.user.is_authenticated else 'anonymous'
            cache_key = make_cache_key(
                f'page_{view_func.__name__}',
                user_id,
                *args,
                **kwargs
            )
            
            # Попытка получить из кэша
            response = cache.get(cache_key)
            
            if response is None:
                response = view_func(request, *args, **kwargs)
                cache.set(cache_key, response, timeout)
                logger.debug(f"Page cached: {cache_key}")
            else:
                logger.debug(f"Page served from cache: {cache_key}")
            
            return response
        return wrapper
    return decorator


def warm_cache(key: str, value: Any, timeout: int = 300) -> bool:
    """
    Предварительный прогрев кэша.
    
    Args:
        key: Ключ кэша
        value: Значение для кэширования
        timeout: Время жизни кэша в секундах
        
    Returns:
        bool: True если успешно, False иначе
    """
    try:
        cache.set(key, value, timeout)
        logger.info(f"Cache warmed: {key}")
        return True
    except Exception as e:
        logger.error(f"Failed to warm cache {key}: {e}")
        return False


def get_or_set_cache(key: str, callback: Callable, timeout: int = 300) -> Any:
    """
    Получает значение из кэша или вычисляет и сохраняет его.
    
    Args:
        key: Ключ кэша
        callback: Функция для вычисления значения если оно не в кэше
        timeout: Время жизни кэша в секундах
        
    Returns:
        Значение из кэша или результат callback
    """
    result = cache.get(key)
    
    if result is None:
        result = callback()
        cache.set(key, result, timeout)
        logger.debug(f"Cache computed and set: {key}")
    else:
        logger.debug(f"Cache retrieved: {key}")
    
    return result

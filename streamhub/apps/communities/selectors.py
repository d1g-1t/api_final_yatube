from apps.communities.models import Community
from common.cache import cache_queryset
import logging

logger = logging.getLogger(__name__)


class CommunitySelector:
    
    @staticmethod
    def get_base_queryset():
        return Community.objects.prefetch_related('members', 'posts')
    
    @staticmethod
    @cache_queryset(timeout=600, key_prefix='community_list')
    def get_active_communities():
        logger.debug("Получение списка активных сообществ")
        return CommunitySelector.get_base_queryset().filter(is_active=True)
    
    @staticmethod
    def get_community_by_id(community_id):
        logger.debug(f"Получение сообщества с ID: {community_id}")
        try:
            return CommunitySelector.get_base_queryset().get(id=community_id, is_active=True)
        except Community.DoesNotExist:
            logger.warning(f"Сообщество с ID {community_id} не найдено")
            raise
    
    @staticmethod
    def get_community_by_slug(slug):
        logger.debug(f"Получение сообщества по слагу: {slug}")
        try:
            return CommunitySelector.get_base_queryset().get(slug=slug, is_active=True)
        except Community.DoesNotExist:
            logger.warning(f"Сообщество с слагом {slug} не найдено")
            raise
    
    @staticmethod
    def get_user_communities(user):
        logger.debug(f"Получение сообществ пользователя: {user.username}")
        return CommunitySelector.get_base_queryset().filter(members=user, is_active=True)

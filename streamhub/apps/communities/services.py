from django.db import transaction
from apps.communities.models import Community
from common.cache import invalidate_cache
from common.exceptions import CommunityNotFoundException
import logging

logger = logging.getLogger(__name__)


class CommunityService:
    
    @staticmethod
    @transaction.atomic
    def create_community(creator, title, description, slug=None, image=None):
        logger.info(f"Создание сообщества пользователем: {creator.username}")
        
        community = Community.objects.create(
            creator=creator,
            title=title,
            description=description,
            slug=slug,
            image=image
        )
        
        community.members.add(creator)
        
        invalidate_cache('community_list')
        logger.info(f"Сообщество создано: {community.id}")
        
        return community
    
    @staticmethod
    @transaction.atomic
    def update_community(community_id, user, **update_data):
        logger.info(f"Обновление сообщества: {community_id}")
        
        try:
            community = Community.objects.select_for_update().get(id=community_id, creator=user)
        except Community.DoesNotExist:
            logger.error(f"Сообщество {community_id} не найдено или доступ запрещен")
            raise CommunityNotFoundException()
        
        for field, value in update_data.items():
            if hasattr(community, field) and field != 'members':
                setattr(community, field, value)
        
        community.save()
        invalidate_cache('community_list')
        logger.info(f"Сообщество {community_id} обновлено")
        
        return community
    
    @staticmethod
    @transaction.atomic
    def join_community(community_id, user):
        logger.info(f"Пользователь {user.username} вступает в сообщество {community_id}")
        
        try:
            community = Community.objects.get(id=community_id, is_active=True)
        except Community.DoesNotExist:
            logger.error(f"Сообщество {community_id} не найдено")
            raise CommunityNotFoundException()
        
        community.members.add(user)
        logger.info(f"Пользователь {user.username} вступил в сообщество {community_id}")
        
        return community
    
    @staticmethod
    @transaction.atomic
    def leave_community(community_id, user):
        logger.info(f"Пользователь {user.username} покидает сообщество {community_id}")
        
        try:
            community = Community.objects.get(id=community_id, is_active=True)
        except Community.DoesNotExist:
            logger.error(f"Сообщество {community_id} не найдено")
            raise CommunityNotFoundException()
        
        community.members.remove(user)
        logger.info(f"Пользователь {user.username} покинул сообщество {community_id}")
        
        return community

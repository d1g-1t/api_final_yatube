from apps.interactions.models import Comment, Subscription
from django.contrib.auth import get_user_model
import logging

User = get_user_model()
logger = logging.getLogger(__name__)


class CommentSelector:
    
    @staticmethod
    def get_base_queryset():
        return Comment.objects.select_related('author', 'post')
    
    @staticmethod
    def get_post_comments(post_id):
        logger.debug(f"Получение комментариев для поста: {post_id}")
        return CommentSelector.get_base_queryset().filter(post_id=post_id)
    
    @staticmethod
    def get_comment_by_id(comment_id):
        logger.debug(f"Получение комментария: {comment_id}")
        try:
            return CommentSelector.get_base_queryset().get(id=comment_id)
        except Comment.DoesNotExist:
            logger.warning(f"Комментарий {comment_id} не найден")
            raise
    
    @staticmethod
    def get_user_comments(user):
        logger.debug(f"Получение комментариев пользователя: {user.username}")
        return CommentSelector.get_base_queryset().filter(author=user)


class SubscriptionSelector:
    
    @staticmethod
    def get_base_queryset():
        return Subscription.objects.select_related('subscriber', 'target')
    
    @staticmethod
    def get_user_subscriptions(user):
        logger.debug(f"Получение подписок пользователя: {user.username}")
        return SubscriptionSelector.get_base_queryset().filter(subscriber=user)
    
    @staticmethod
    def get_user_subscribers(user):
        logger.debug(f"Получение подписчиков пользователя: {user.username}")
        return SubscriptionSelector.get_base_queryset().filter(target=user)
    
    @staticmethod
    def is_subscribed(subscriber, target):
        return Subscription.objects.filter(subscriber=subscriber, target=target).exists()

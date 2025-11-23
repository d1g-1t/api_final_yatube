from django.db import transaction, IntegrityError
from .models import Comment, Subscription
import logging

logger = logging.getLogger(__name__)


class CommentService:
    @staticmethod
    @transaction.atomic
    def create_comment(post, author, content):
        comment = Comment.objects.create(
            post=post,
            author=author,
            content=content
        )
        logger.info(f"Создан комментарий ID:{comment.id} к посту ID:{post.id}")
        return comment
    
    @staticmethod
    @transaction.atomic
    def update_comment(comment, content):
        comment.content = content
        comment.save(update_fields=['content', 'updated_at'])
        logger.info(f"Обновлен комментарий ID:{comment.id}")
        return comment
    
    @staticmethod
    @transaction.atomic
    def delete_comment(comment):
        comment_id = comment.id
        comment.delete()
        logger.info(f"Удален комментарий ID:{comment_id}")


class SubscriptionService:
    @staticmethod
    @transaction.atomic
    def subscribe(subscriber, target_user):
        try:
            subscription = Subscription.objects.create(
                subscriber=subscriber,
                target_user=target_user
            )
            logger.info(f"{subscriber.username} подписался на {target_user.username}")
            return subscription
        except IntegrityError:
            logger.warning(f"Попытка повторной подписки {subscriber.username} на {target_user.username}")
            raise ValueError("Вы уже подписаны на этого пользователя")
    
    @staticmethod
    @transaction.atomic
    def unsubscribe(subscriber, target_user):
        deleted, _ = Subscription.objects.filter(
            subscriber=subscriber,
            target_user=target_user
        ).delete()
        if deleted:
            logger.info(f"{subscriber.username} отписался от {target_user.username}")
        return deleted > 0

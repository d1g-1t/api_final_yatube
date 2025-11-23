from django.contrib.auth import get_user_model
import logging

User = get_user_model()
logger = logging.getLogger(__name__)


class UserSelector:
    
    @staticmethod
    def get_user_by_username(username):
        logger.debug(f"Получение пользователя: {username}")
        try:
            return User.objects.get(username=username)
        except User.DoesNotExist:
            logger.warning(f"Пользователь {username} не найден")
            raise
    
    @staticmethod
    def get_user_by_id(user_id):
        logger.debug(f"Получение пользователя с ID: {user_id}")
        try:
            return User.objects.get(id=user_id)
        except User.DoesNotExist:
            logger.warning(f"Пользователь с ID {user_id} не найден")
            raise

from django.contrib.auth import get_user_model
import logging

User = get_user_model()
logger = logging.getLogger(__name__)


class UserService:
    
    @staticmethod
    def create_user(username, email, password):
        logger.info(f"Создание пользователя: {username}")
        
        user = User.objects.create_user(
            username=username,
            email=email,
            password=password
        )
        
        logger.info(f"Пользователь создан: {user.username}")
        return user

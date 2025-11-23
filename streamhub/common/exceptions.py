import logging
from rest_framework.views import exception_handler
from rest_framework.response import Response
from rest_framework import status

logger = logging.getLogger(__name__)


def custom_exception_handler(exc, context):
    response = exception_handler(exc, context)

    if response is not None:
        logger.error(
            f"Ошибка API: {exc.__class__.__name__} - {str(exc)}",
            extra={'context': context}
        )
        
        custom_response_data = {
            'error': response.data,
            'status_code': response.status_code
        }
        response.data = custom_response_data

    return response


class BusinessLogicException(Exception):
    default_message = "Произошла ошибка бизнес-логики"

    def __init__(self, message=None):
        self.message = message or self.default_message
        super().__init__(self.message)


class PostNotFoundException(BusinessLogicException):
    default_message = "Пост не найден"


class CommunityNotFoundException(BusinessLogicException):
    default_message = "Сообщество не найдено"


class CommentNotFoundException(BusinessLogicException):
    default_message = "Комментарий не найден"


class SubscriptionAlreadyExistsException(BusinessLogicException):
    default_message = "Подписка уже существует"


class SelfSubscriptionException(BusinessLogicException):
    default_message = "Невозможно подписаться на самого себя"

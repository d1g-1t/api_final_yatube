"""
Базовые абстрактные модели для всех приложений.
Следуют принципам DRY и обеспечивают единообразие данных.
"""
import uuid
from django.db import models
from django.utils import timezone


class TimeStampedModel(models.Model):
    """
    Абстрактная модель с полями временных меток.
    Автоматически отслеживает время создания и обновления.
    """
    created_at = models.DateTimeField(
        auto_now_add=True,
        db_index=True,
        verbose_name="Дата создания"
    )
    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name="Дата обновления"
    )

    class Meta:
        abstract = True
        ordering = ['-created_at']


class UUIDModel(models.Model):
    """
    Абстрактная модель с UUID в качестве первичного ключа.
    Обеспечивает безопасность и масштабируемость.
    """
    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False
    )

    class Meta:
        abstract = True


class SoftDeleteModel(models.Model):
    """
    Абстрактная модель с поддержкой мягкого удаления.
    Позволяет восстанавливать удаленные записи.
    """
    is_deleted = models.BooleanField(
        default=False,
        db_index=True,
        verbose_name="Удалено"
    )
    deleted_at = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name="Дата удаления"
    )

    class Meta:
        abstract = True

    def soft_delete(self):
        """Мягкое удаление записи"""
        self.is_deleted = True
        self.deleted_at = timezone.now()
        self.save(update_fields=['is_deleted', 'deleted_at'])

    def restore(self):
        """Восстановление удаленной записи"""
        self.is_deleted = False
        self.deleted_at = None
        self.save(update_fields=['is_deleted', 'deleted_at'])


class BaseModel(TimeStampedModel, SoftDeleteModel):
    """
    Базовая модель объединяющая временные метки и мягкое удаление.
    Рекомендуется для большинства моделей приложения.
    """
    
    class Meta:
        abstract = True

    def __repr__(self):
        return f"<{self.__class__.__name__}(id={self.pk})>"

from django.db import models
from django.contrib.auth import get_user_model
from django.core.validators import MinLengthValidator
from django.utils.text import slugify

User = get_user_model()


class Community(models.Model):
    title = models.CharField(
        max_length=200,
        unique=True,
        verbose_name='Название',
        validators=[MinLengthValidator(3)]
    )
    slug = models.SlugField(
        max_length=200,
        unique=True,
        verbose_name='Слаг',
        db_index=True
    )
    description = models.TextField(
        verbose_name='Описание',
        validators=[MinLengthValidator(10)]
    )
    image = models.ImageField(
        upload_to='communities/',
        null=True,
        blank=True,
        verbose_name='Изображение'
    )
    creator = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        related_name='created_communities',
        verbose_name='Создатель'
    )
    members = models.ManyToManyField(
        User,
        related_name='communities',
        verbose_name='Участники',
        blank=True
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Дата создания',
        db_index=True
    )
    is_active = models.BooleanField(
        default=True,
        verbose_name='Активно',
        db_index=True
    )

    class Meta:
        ordering = ['title']
        verbose_name = 'Сообщество'
        verbose_name_plural = 'Сообщества'
        indexes = [
            models.Index(fields=['slug']),
            models.Index(fields=['-created_at']),
        ]

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)
        super().save(*args, **kwargs)

from rest_framework import viewsets, permissions, filters
from rest_framework.viewsets import GenericViewSet
from rest_framework.generics import get_object_or_404
from rest_framework.mixins import CreateModelMixin, ListModelMixin
from rest_framework.pagination import LimitOffsetPagination

from posts.models import Group, Post
from api.permissions import IsAuthorOrReadOnly
from api.serializers import (
    PostSerializer, GroupSerializer, CommentSerializer, FollowSerializer
)


class PostViewSet(viewsets.ModelViewSet):
    """
    Вьюсет для модели Post.
    Позволяет выполнять CRUD операции с постами.
    """
    queryset = Post.objects.all().select_related('author')
    serializer_class = PostSerializer
    permission_classes = (IsAuthorOrReadOnly,)
    pagination_class = LimitOffsetPagination

    def perform_create(self, serializer):
        """
        Переопределяет метод сохранения для добавления автора поста.
        """
        serializer.save(author=self.request.user)


class GroupViewSet(viewsets.ReadOnlyModelViewSet):
    """
    Вьюсет для модели Group.
    Позволяет только чтение групп.
    """
    queryset = Group.objects.all()
    serializer_class = GroupSerializer
    permission_classes = (permissions.IsAuthenticatedOrReadOnly,)


class CommentViewSet(viewsets.ModelViewSet):
    """
    Вьюсет для модели Comment.
    Позволяет выполнять CRUD операции с комментариями.
    """
    serializer_class = CommentSerializer
    permission_classes = (IsAuthorOrReadOnly,)

    def perform_create(self, serializer):
        """
        Переопределяет метод сохранения для добавления автора и поста.
        """
        serializer.save(
            author=self.request.user,
            post=self.get_post()
        )

    def get_post(self):
        """
        Получает объект поста по его ID из URL.
        """
        return get_object_or_404(
            Post,
            pk=self.kwargs.get('post_id')
        )

    def get_queryset(self):
        """
        Возвращает комментарии для текущего поста.
        """
        return self.get_post().comments.select_related('author')


class FollowViewSet(CreateModelMixin, ListModelMixin, GenericViewSet):
    """
    Вьюсет для модели Follow.
    Позволяет создавать и просматривать подписки.
    """
    serializer_class = FollowSerializer
    filter_backends = (filters.SearchFilter,)
    search_fields = ('following__username',)

    def perform_create(self, serializer):
        """
        Переопределяет метод сохранения для добавления пользователя.
        """
        serializer.save(user=self.request.user)

    def get_queryset(self):
        """
        Возвращает подписки текущего пользователя.
        """
        return self.request.user.follower.all()

from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticatedOrReadOnly
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter, OrderingFilter

from apps.posts.models import Post
from apps.posts.selectors import PostSelector
from apps.posts.services import PostService
from apps.posts.api.serializers import (
    PostListSerializer,
    PostDetailSerializer,
    PostCreateUpdateSerializer
)
from apps.posts.api.filters import PostFilter
from common.permissions import IsAuthorOrReadOnly
from common.pagination import PostPagination
import logging

logger = logging.getLogger(__name__)


class PostViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticatedOrReadOnly, IsAuthorOrReadOnly]
    pagination_class = PostPagination
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_class = PostFilter
    search_fields = ['title', 'content']
    ordering_fields = ['created_at', 'views_count']
    ordering = ['-created_at']
    
    def get_queryset(self):
        return PostSelector.get_published_posts()
    
    def get_serializer_class(self):
        if self.action == 'list':
            return PostListSerializer
        elif self.action in ['create', 'update', 'partial_update']:
            return PostCreateUpdateSerializer
        return PostDetailSerializer
    
    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        PostService.increment_view_count(instance.id)
        logger.info(f"Просмотр поста: {instance.id}")
        serializer = self.get_serializer(instance)
        return Response(serializer.data)
    
    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        post = PostService.create_post(
            author=request.user,
            **serializer.validated_data
        )
        
        logger.info(f"Создан новый пост: {post.id} пользователем {request.user.username}")
        output_serializer = PostDetailSerializer(post)
        return Response(output_serializer.data, status=status.HTTP_201_CREATED)
    
    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        
        updated_post = PostService.update_post(
            post_id=instance.id,
            author=request.user,
            **serializer.validated_data
        )
        
        logger.info(f"Обновлен пост: {updated_post.id}")
        output_serializer = PostDetailSerializer(updated_post)
        return Response(output_serializer.data)
    
    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        PostService.delete_post(post_id=instance.id, author=request.user)
        logger.info(f"Удален пост: {instance.id}")
        return Response(status=status.HTTP_204_NO_CONTENT)
    
    @action(detail=False, methods=['get'])
    def my_posts(self, request):
        posts = PostSelector.get_posts_by_author(request.user)
        page = self.paginate_queryset(posts)
        
        if page is not None:
            serializer = PostListSerializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        
        serializer = PostListSerializer(posts, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def feed(self, request):
        posts = PostSelector.get_user_feed(request.user)
        page = self.paginate_queryset(posts)
        
        if page is not None:
            serializer = PostListSerializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        
        serializer = PostListSerializer(posts, many=True)
        return Response(serializer.data)

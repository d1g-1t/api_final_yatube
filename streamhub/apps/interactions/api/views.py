from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated

from apps.interactions.models import Comment, Subscription
from apps.interactions.selectors import CommentSelector, SubscriptionSelector
from apps.interactions.services import CommentService, SubscriptionService
from apps.interactions.api.serializers import (
    CommentSerializer,
    CommentCreateUpdateSerializer,
    SubscriptionSerializer
)
from common.permissions import IsAuthorOrReadOnly
from common.pagination import StandardResultsSetPagination
import logging

logger = logging.getLogger(__name__)


class CommentViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated, IsAuthorOrReadOnly]
    pagination_class = StandardResultsSetPagination
    
    def get_queryset(self):
        post_id = self.kwargs.get('post_id')
        if post_id:
            return CommentSelector.get_post_comments(post_id)
        return CommentSelector.get_base_queryset()
    
    def get_serializer_class(self):
        if self.action in ['create', 'update', 'partial_update']:
            return CommentCreateUpdateSerializer
        return CommentSerializer
    
    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        post_id = self.kwargs.get('post_id')
        comment = CommentService.create_comment(
            author=request.user,
            post_id=post_id,
            content=serializer.validated_data['content']
        )
        
        logger.info(f"Создан комментарий: {comment.pk}")
        output_serializer = CommentSerializer(comment)
        return Response(output_serializer.data, status=status.HTTP_201_CREATED)
    
    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        
        updated_comment = CommentService.update_comment(
            comment_id=instance.id,
            author=request.user,
            content=serializer.validated_data['content']
        )
        
        logger.info(f"Обновлен комментарий: {updated_comment.pk}")
        output_serializer = CommentSerializer(updated_comment)
        return Response(output_serializer.data)
    
    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        CommentService.delete_comment(comment_id=instance.id, author=request.user)
        logger.info(f"Удален комментарий: {instance.id}")
        return Response(status=status.HTTP_204_NO_CONTENT)


class SubscriptionViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated]
    serializer_class = SubscriptionSerializer
    pagination_class = StandardResultsSetPagination
    http_method_names = ['get', 'post', 'delete']
    
    def get_queryset(self):
        return SubscriptionSelector.get_user_subscriptions(self.request.user)
    
    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        subscription = SubscriptionService.create_subscription(
            subscriber=request.user,
            target_username=serializer.validated_data['target']['username']
        )
        
        logger.info(f"Создана подписка: {subscription.pk}")
        output_serializer = SubscriptionSerializer(subscription)
        return Response(output_serializer.data, status=status.HTTP_201_CREATED)
    
    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        SubscriptionService.delete_subscription(
            subscriber=request.user,
            target_username=instance.target.username
        )
        logger.info(f"Удалена подписка: {instance.id}")
        return Response(status=status.HTTP_204_NO_CONTENT)
    
    @action(detail=False, methods=['get'])
    def subscribers(self, request):
        subscribers = SubscriptionSelector.get_user_subscribers(request.user)
        page = self.paginate_queryset(subscribers)
        
        if page is not None:
            serializer = SubscriptionSerializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        
        serializer = SubscriptionSerializer(subscribers, many=True)
        return Response(serializer.data)

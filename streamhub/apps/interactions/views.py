from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.shortcuts import get_object_or_404
from .models import Comment, Subscription
from .serializers import CommentSerializer, SubscriptionSerializer
from .services import CommentService, SubscriptionService
from apps.posts.models import Post
from common.permissions import IsAuthorOrReadOnly


class CommentViewSet(viewsets.ModelViewSet):
    serializer_class = CommentSerializer
    permission_classes = [IsAuthorOrReadOnly]
    
    def get_queryset(self):
        post_id = self.kwargs.get('post_id')
        return Comment.objects.filter(
            post_id=post_id
        ).select_related('author').order_by('-created_at')
    
    def get_serializer_context(self):
        context = super().get_serializer_context()
        context['post_id'] = self.kwargs.get('post_id')
        return context
    
    def perform_create(self, serializer):
        post = get_object_or_404(Post, pk=self.kwargs.get('post_id'))
        comment = CommentService.create_comment(
            post=post,
            author=self.request.user,
            content=serializer.validated_data['content']
        )
        serializer.instance = comment
    
    def perform_update(self, serializer):
        comment = CommentService.update_comment(
            serializer.instance,
            serializer.validated_data['content']
        )
        serializer.instance = comment
    
    def perform_destroy(self, instance):
        CommentService.delete_comment(instance)


class SubscriptionViewSet(viewsets.ModelViewSet):
    serializer_class = SubscriptionSerializer
    permission_classes = [IsAuthenticated]
    http_method_names = ['get', 'post', 'delete']
    
    def get_queryset(self):
        return Subscription.objects.filter(
            subscriber=self.request.user
        ).select_related('target_user')
    
    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        try:
            subscription = SubscriptionService.subscribe(
                subscriber=request.user,
                target_user=serializer.validated_data['target_username']
            )
            output_serializer = self.get_serializer(subscription)
            return Response(output_serializer.data, status=status.HTTP_201_CREATED)
        except ValueError as e:
            return Response({'detail': str(e)}, status=status.HTTP_400_BAD_REQUEST)
    
    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        if instance.subscriber != request.user:
            return Response(
                {'detail': 'Вы не можете отменить чужую подписку'},
                status=status.HTTP_403_FORBIDDEN
            )
        SubscriptionService.unsubscribe(instance.subscriber, instance.target_user)
        return Response(status=status.HTTP_204_NO_CONTENT)

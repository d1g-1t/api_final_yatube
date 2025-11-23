from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticatedOrReadOnly, IsAuthenticated

from apps.communities.models import Community
from apps.communities.selectors import CommunitySelector
from apps.communities.services import CommunityService
from apps.communities.api.serializers import (
    CommunityListSerializer,
    CommunityDetailSerializer,
    CommunityCreateUpdateSerializer
)
from apps.posts.selectors import PostSelector
from apps.posts.api.serializers import PostListSerializer
from common.pagination import StandardResultsSetPagination
import logging

logger = logging.getLogger(__name__)


class CommunityViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticatedOrReadOnly]
    pagination_class = StandardResultsSetPagination
    lookup_field = 'slug'
    
    def get_queryset(self):
        return CommunitySelector.get_active_communities()
    
    def get_serializer_class(self):
        if self.action == 'list':
            return CommunityListSerializer
        elif self.action in ['create', 'update', 'partial_update']:
            return CommunityCreateUpdateSerializer
        return CommunityDetailSerializer
    
    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        community = CommunityService.create_community(
            creator=request.user,
            **serializer.validated_data
        )
        
        logger.info(f"Создано сообщество: {community.slug} пользователем {request.user.username}")
        output_serializer = CommunityDetailSerializer(community)
        return Response(output_serializer.data, status=status.HTTP_201_CREATED)
    
    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        
        updated_community = CommunityService.update_community(
            community_id=instance.id,
            user=request.user,
            **serializer.validated_data
        )
        
        logger.info(f"Обновлено сообщество: {updated_community.slug}")
        output_serializer = CommunityDetailSerializer(updated_community)
        return Response(output_serializer.data)
    
    @action(detail=True, methods=['post'], permission_classes=[IsAuthenticated])
    def join(self, request, slug=None):
        community = self.get_object()
        CommunityService.join_community(community.id, request.user)
        logger.info(f"Пользователь {request.user.username} вступил в {community.slug}")
        return Response({'detail': 'Вы вступили в сообщество'}, status=status.HTTP_200_OK)
    
    @action(detail=True, methods=['post'], permission_classes=[IsAuthenticated])
    def leave(self, request, slug=None):
        community = self.get_object()
        CommunityService.leave_community(community.id, request.user)
        logger.info(f"Пользователь {request.user.username} покинул {community.slug}")
        return Response({'detail': 'Вы покинули сообщество'}, status=status.HTTP_200_OK)
    
    @action(detail=True, methods=['get'])
    def posts(self, request, slug=None):
        community = self.get_object()
        posts = PostSelector.get_posts_by_community(community.id)
        page = self.paginate_queryset(posts)
        
        if page is not None:
            serializer = PostListSerializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        
        serializer = PostListSerializer(posts, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'], permission_classes=[IsAuthenticated])
    def my_communities(self, request):
        communities = CommunitySelector.get_user_communities(request.user)
        page = self.paginate_queryset(communities)
        
        if page is not None:
            serializer = CommunityListSerializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        
        serializer = CommunityListSerializer(communities, many=True)
        return Response(serializer.data)

from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from django.shortcuts import get_object_or_404
from .models import Post, Community
from .serializers import PostListSerializer, PostCreateSerializer, CommunitySerializer
from .services import PostService, CommunityService
from .selectors import PostSelector, CommunitySelector
from common.permissions import IsAuthorOrReadOnly
import logging

logger = logging.getLogger(__name__)


class PostViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthorOrReadOnly]
    
    def get_queryset(self):
        if self.action == 'list':
            return PostSelector.get_published_posts()
        return PostSelector.get_optimized_queryset()
    
    def get_serializer_class(self):
        if self.action in ['create', 'update', 'partial_update']:
            return PostCreateSerializer
        return PostListSerializer
    
    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        PostService.increment_views(instance)
        serializer = self.get_serializer(instance)
        return Response(serializer.data)
    
    def perform_create(self, serializer):
        post = PostService.create_post(
            author=self.request.user,
            **serializer.validated_data
        )
        serializer.instance = post
    
    def perform_update(self, serializer):
        post = PostService.update_post(
            serializer.instance,
            **serializer.validated_data
        )
        serializer.instance = post
    
    def perform_destroy(self, instance):
        PostService.delete_post(instance)
    
    @action(detail=False, methods=['get'], permission_classes=[IsAuthenticated])
    def my_posts(self, request):
        posts = PostSelector.get_user_posts(request.user)
        page = self.paginate_queryset(posts)
        serializer = self.get_serializer(page, many=True)
        return self.get_paginated_response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def search(self, request):
        query = request.query_params.get('q', '')
        if len(query) < 3:
            return Response(
                {'detail': 'Поисковый запрос должен содержать минимум 3 символа'},
                status=status.HTTP_400_BAD_REQUEST
            )
        posts = PostSelector.search_posts(query)
        page = self.paginate_queryset(posts)
        serializer = self.get_serializer(page, many=True)
        return self.get_paginated_response(serializer.data)


class CommunityViewSet(viewsets.ModelViewSet):
    queryset = CommunitySelector.get_all_communities()
    serializer_class = CommunitySerializer
    lookup_field = 'slug'
    permission_classes = [IsAuthenticated]
    
    def get_permissions(self):
        if self.action in ['list', 'retrieve']:
            return [AllowAny()]
        return super().get_permissions()
    
    def perform_create(self, serializer):
        community = CommunityService.create_community(**serializer.validated_data)
        serializer.instance = community
    
    @action(detail=True, methods=['get'])
    def posts(self, request, slug=None):
        posts = PostSelector.get_community_posts(slug)
        page = self.paginate_queryset(posts)
        serializer = PostListSerializer(page, many=True, context={'request': request})
        return self.get_paginated_response(serializer.data)

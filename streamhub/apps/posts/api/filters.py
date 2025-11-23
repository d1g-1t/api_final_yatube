from django_filters import rest_framework as filters
from apps.posts.models import Post


class PostFilter(filters.FilterSet):
    title = filters.CharFilter(lookup_expr='icontains')
    author_username = filters.CharFilter(field_name='author__username', lookup_expr='icontains')
    community = filters.NumberFilter(field_name='community__id')
    created_after = filters.DateTimeFilter(field_name='created_at', lookup_expr='gte')
    created_before = filters.DateTimeFilter(field_name='created_at', lookup_expr='lte')
    
    class Meta:
        model = Post
        fields = ['title', 'author_username', 'community', 'created_after', 'created_before']

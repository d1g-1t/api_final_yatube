from rest_framework import serializers
from .models import Post, Community
from django.contrib.auth import get_user_model

User = get_user_model()


class AuthorSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'first_name', 'last_name']


class CommunitySerializer(serializers.ModelSerializer):
    posts_count = serializers.SerializerMethodField()
    
    class Meta:
        model = Community
        fields = ['id', 'title', 'slug', 'description', 'created_at', 'posts_count']
        lookup_field = 'slug'
    
    def get_posts_count(self, obj):
        return obj.posts.filter(is_published=True).count()


class PostListSerializer(serializers.ModelSerializer):
    author = AuthorSerializer(read_only=True)
    community = serializers.SlugRelatedField(
        slug_field='slug',
        queryset=Community.objects.all(),
        required=False
    )
    comments_count = serializers.SerializerMethodField()
    
    class Meta:
        model = Post
        fields = [
            'id', 'title', 'content', 'author', 'community',
            'image', 'created_at', 'views_count', 'comments_count'
        ]
        read_only_fields = ['author', 'created_at', 'views_count']
    
    def get_comments_count(self, obj):
        return getattr(obj, 'comments_count', 0)


class PostCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Post
        fields = ['title', 'content', 'community', 'image']
    
    def create(self, validated_data):
        validated_data['author'] = self.context['request'].user
        return super().create(validated_data)

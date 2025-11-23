from rest_framework import serializers
from apps.posts.models import Post


class PostListSerializer(serializers.ModelSerializer):
    author_username = serializers.CharField(source='author.username', read_only=True)
    community_title = serializers.CharField(source='community.title', read_only=True, allow_null=True)
    comments_count = serializers.SerializerMethodField()
    
    class Meta:
        model = Post
        fields = [
            'id', 'title', 'content', 'author_username', 
            'community_title', 'created_at', 'views_count', 
            'comments_count', 'image'
        ]
        read_only_fields = ['id', 'created_at', 'views_count']
    
    def get_comments_count(self, obj):
        return obj.comments.count() if hasattr(obj, 'comments') else 0


class PostDetailSerializer(serializers.ModelSerializer):
    author_username = serializers.CharField(source='author.username', read_only=True)
    community_title = serializers.CharField(source='community.title', read_only=True, allow_null=True)
    
    class Meta:
        model = Post
        fields = [
            'id', 'title', 'content', 'author_username', 
            'community', 'community_title', 'image', 
            'created_at', 'updated_at', 'views_count'
        ]
        read_only_fields = ['id', 'author_username', 'created_at', 'updated_at', 'views_count']


class PostCreateUpdateSerializer(serializers.ModelSerializer):
    
    class Meta:
        model = Post
        fields = ['title', 'content', 'image', 'community']
    
    def validate_title(self, value):
        if len(value) < 3:
            raise serializers.ValidationError("Заголовок должен содержать минимум 3 символа")
        return value
    
    def validate_content(self, value):
        if len(value) < 10:
            raise serializers.ValidationError("Содержание должно содержать минимум 10 символов")
        return value

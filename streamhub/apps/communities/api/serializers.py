from rest_framework import serializers
from apps.communities.models import Community


class CommunityListSerializer(serializers.ModelSerializer):
    members_count = serializers.SerializerMethodField()
    posts_count = serializers.SerializerMethodField()
    
    class Meta:
        model = Community
        fields = ['id', 'title', 'slug', 'description', 'image', 'members_count', 'posts_count', 'created_at']
        read_only_fields = ['id', 'slug', 'created_at']
    
    def get_members_count(self, obj):
        return obj.members.count()
    
    def get_posts_count(self, obj):
        return obj.posts.filter(is_published=True).count() if hasattr(obj, 'posts') else 0


class CommunityDetailSerializer(serializers.ModelSerializer):
    creator_username = serializers.CharField(source='creator.username', read_only=True, allow_null=True)
    members_count = serializers.SerializerMethodField()
    posts_count = serializers.SerializerMethodField()
    
    class Meta:
        model = Community
        fields = [
            'id', 'title', 'slug', 'description', 'image', 
            'creator_username', 'members_count', 'posts_count', 
            'created_at', 'is_active'
        ]
        read_only_fields = ['id', 'slug', 'creator_username', 'created_at']
    
    def get_members_count(self, obj):
        return obj.members.count()
    
    def get_posts_count(self, obj):
        return obj.posts.filter(is_published=True).count() if hasattr(obj, 'posts') else 0


class CommunityCreateUpdateSerializer(serializers.ModelSerializer):
    
    class Meta:
        model = Community
        fields = ['title', 'description', 'image']
    
    def validate_title(self, value):
        if len(value) < 3:
            raise serializers.ValidationError("Название должно содержать минимум 3 символа")
        return value
    
    def validate_description(self, value):
        if len(value) < 10:
            raise serializers.ValidationError("Описание должно содержать минимум 10 символов")
        return value

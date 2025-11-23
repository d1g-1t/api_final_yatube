from rest_framework import serializers
from .models import Comment, Subscription
from apps.posts.serializers import AuthorSerializer


class CommentSerializer(serializers.ModelSerializer):
    author = AuthorSerializer(read_only=True)
    
    class Meta:
        model = Comment
        fields = ['id', 'post', 'author', 'content', 'created_at', 'updated_at']
        read_only_fields = ['post', 'author', 'created_at', 'updated_at']
    
    def create(self, validated_data):
        validated_data['author'] = self.context['request'].user
        validated_data['post_id'] = self.context['post_id']
        return super().create(validated_data)


class SubscriptionSerializer(serializers.ModelSerializer):
    subscriber = AuthorSerializer(read_only=True)
    target_user = AuthorSerializer(read_only=True)
    target_username = serializers.CharField(write_only=True)
    
    class Meta:
        model = Subscription
        fields = ['id', 'subscriber', 'target_user', 'target_username', 'created_at']
        read_only_fields = ['subscriber', 'created_at']
    
    def validate_target_username(self, value):
        from django.contrib.auth import get_user_model
        User = get_user_model()
        
        try:
            target = User.objects.get(username=value)
        except User.DoesNotExist:
            raise serializers.ValidationError("Пользователь не найден")
        
        if target == self.context['request'].user:
            raise serializers.ValidationError("Нельзя подписаться на себя")
        
        return target
    
    def create(self, validated_data):
        target = validated_data.pop('target_username')
        return Subscription.objects.create(
            subscriber=self.context['request'].user,
            target_user=target
        )

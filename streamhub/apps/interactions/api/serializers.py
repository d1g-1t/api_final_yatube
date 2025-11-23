from rest_framework import serializers
from apps.interactions.models import Comment, Subscription


class CommentSerializer(serializers.ModelSerializer):
    author_username = serializers.CharField(source='author.username', read_only=True)
    post_id = serializers.IntegerField(read_only=True)
    
    class Meta:
        model = Comment
        fields = ['id', 'author_username', 'post_id', 'content', 'created_at', 'updated_at']
        read_only_fields = ['id', 'author_username', 'post_id', 'created_at', 'updated_at']


class CommentCreateUpdateSerializer(serializers.ModelSerializer):
    
    class Meta:
        model = Comment
        fields = ['content']
    
    def validate_content(self, value):
        if len(value) < 2:
            raise serializers.ValidationError("Комментарий должен содержать минимум 2 символа")
        return value


class SubscriptionSerializer(serializers.ModelSerializer):
    subscriber_username = serializers.CharField(source='subscriber.username', read_only=True)
    target_username = serializers.CharField(source='target.username')
    
    class Meta:
        model = Subscription
        fields = ['id', 'subscriber_username', 'target_username', 'created_at']
        read_only_fields = ['id', 'subscriber_username', 'created_at']

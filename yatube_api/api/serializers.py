from rest_framework import serializers
from rest_framework.relations import SlugRelatedField
from rest_framework.validators import UniqueTogetherValidator

from posts.models import Post, Comment, Group, Follow, User


class GroupSerializer(serializers.ModelSerializer):
    """Сериалайзер для модели Group."""
    class Meta:
        model = Group
        fields = '__all__'


class PostSerializer(serializers.ModelSerializer):
    """Сериалайзер для модели Post."""

    DATE_FORMAT = "%Y-%m-%d %H:%M:%S"

    author = SlugRelatedField(
        default=serializers.CurrentUserDefault(),
        read_only=True,
        slug_field='username'
    )
    pub_date = serializers.DateTimeField(
        read_only=True,
        format=DATE_FORMAT
    )

    class Meta:
        model = Post
        fields = '__all__'


class CommentSerializer(serializers.ModelSerializer):
    """Сериалайзер для модели Comment."""
    author = SlugRelatedField(
        read_only=True,
        slug_field='username'
    )

    class Meta:
        model = Comment
        fields = '__all__'
        read_only_fields = ('post',)


class FollowSerializer(serializers.ModelSerializer):
    """Сериалайзер для модели Follow."""

    ERROR_SELF_FOLLOW = "Нельзя подписаться на себя."

    user = SlugRelatedField(
        default=serializers.CurrentUserDefault(),
        read_only=True,
        slug_field='username'
    )
    following = SlugRelatedField(
        queryset=User.objects.all(),
        slug_field='username'
    )

    def validate(self, data):
        """
        Выбрасываем исключение, когда пользователь
        хочет подписаться сам на себя.
        """
        if self.context['request'].user == data['following']:
            raise serializers.ValidationError(self.ERROR_SELF_FOLLOW)
        return data

    class Meta:
        model = Follow
        fields = '__all__'
        validators = (
            (UniqueTogetherValidator(
                queryset=Follow.objects.all(),
                fields=('user', 'following'),
            )),
        )

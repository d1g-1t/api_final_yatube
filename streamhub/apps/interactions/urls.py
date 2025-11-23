from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import CommentViewSet, SubscriptionViewSet

router = DefaultRouter()
router.register(
    r'posts/(?P<post_id>\d+)/comments',
    CommentViewSet,
    basename='comment'
)
router.register('subscriptions', SubscriptionViewSet, basename='subscription')

urlpatterns = [
    path('', include(router.urls)),
]

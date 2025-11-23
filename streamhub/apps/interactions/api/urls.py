from django.urls import path, include
from rest_framework.routers import DefaultRouter
from apps.interactions.api.views import CommentViewSet, SubscriptionViewSet

router = DefaultRouter()
router.register(r'posts/(?P<post_id>\d+)/comments', CommentViewSet, basename='comment')
router.register(r'subscriptions', SubscriptionViewSet, basename='subscription')

urlpatterns = [
    path('', include(router.urls)),
]

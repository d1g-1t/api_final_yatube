from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import PostViewSet, CommunityViewSet

router = DefaultRouter()
router.register('posts', PostViewSet, basename='post')
router.register('communities', CommunityViewSet, basename='community')

urlpatterns = [
    path('', include(router.urls)),
]

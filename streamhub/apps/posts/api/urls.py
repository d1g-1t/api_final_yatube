from django.urls import path, include
from rest_framework.routers import DefaultRouter
from apps.posts.api.views import PostViewSet

router = DefaultRouter()
router.register(r'posts', PostViewSet, basename='post')

urlpatterns = [
    path('', include(router.urls)),
]

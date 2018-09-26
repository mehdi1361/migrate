from rest_framework.routers import DefaultRouter

from .views import UserViewSet, AccountViewSet, ProfileViewSet, CategoryViewSet

router = DefaultRouter()
router.register(r'user', UserViewSet)
router.register(r'account', AccountViewSet)
router.register(r'profile', ProfileViewSet)
router.register(r'category', CategoryViewSet)

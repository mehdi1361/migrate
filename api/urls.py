from rest_framework.routers import DefaultRouter

from .views import UserViewSet, AccountViewSet

router = DefaultRouter()
router.register(r'user', UserViewSet)
router.register(r'account', AccountViewSet)

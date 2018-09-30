from rest_framework.routers import DefaultRouter

from .views import UserViewSet, AccountViewSet, \
    ProfileViewSet, CategoryViewSet, OrderViewSet, PeriodViewSet, OrderMessageViewSet

router = DefaultRouter()
router.register(r'user', UserViewSet)
router.register(r'account', AccountViewSet)
router.register(r'profile', ProfileViewSet)
router.register(r'category', CategoryViewSet)
router.register(r'order', OrderViewSet)
router.register(r'time', PeriodViewSet)
router.register(r'message', OrderMessageViewSet)

from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import UserViewSet, change_password

router = DefaultRouter()
router.register('users', UserViewSet, basename='user')

urlpatterns = [
    path('', include(router.urls)),
    path("change-password/", change_password, name="change-password"),
]

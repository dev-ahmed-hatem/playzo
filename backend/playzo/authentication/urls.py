from django.urls import path
from .views import get_authenticated_user, LoginView, CustomTokenRefreshView, CustomTokenVerifyView

urlpatterns = [
    path('login/', LoginView.as_view(), name='login'),
    path('refresh/', CustomTokenRefreshView.as_view(), name='refresh'),
    path('verify/', CustomTokenVerifyView.as_view(), name='verify'),
    path('authenticated-user/', get_authenticated_user, name='authenticated_user'),
]

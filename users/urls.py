from django.urls import path, include
from .views import RegisterView, UserUpdateView, protected_view, UserInfoViewSet
from rest_framework.routers import DefaultRouter

router = DefaultRouter()
router.register(r'user-info', UserInfoViewSet, basename='user-info')

urlpatterns = [
    path('register/', RegisterView.as_view(), name='register'),
    path('profile/<int:pk>/', UserUpdateView.as_view(), name='update-profile'),
    path('protected/', protected_view, name='protected'),
    path('', include(router.urls)),
]

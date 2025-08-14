from django.urls import path
from .views import RegisterView, UserUpdateView

urlpatterns = [
    path('register/', RegisterView.as_view(), name='register'),
    path('profile/<int:pk>/', UserUpdateView.as_view(), name='update-profile'),
]
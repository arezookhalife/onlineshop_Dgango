from django.urls import path
from .views import RegisterView, UserUpdateView, protected_view

urlpatterns = [
    path('register/', RegisterView.as_view(), name='register'),
    path('profile/<int:pk>/', UserUpdateView.as_view(), name='update-profile'),
    path('protected/', protected_view, name='protected'),
]

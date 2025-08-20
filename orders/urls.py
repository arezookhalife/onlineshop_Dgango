from django.urls import path
from rest_framework.routers import DefaultRouter
from .views import OrderViewSet
from .views import checkout, payment_callback


router = DefaultRouter()
router.register(r'orders', OrderViewSet, basename='order')

urlpatterns = router.urls+[
    path('checkout/', checkout, name='checkout'),
    path('payment/callback/', payment_callback, name='payment-callback'),
]
from django.urls import path
from .views import CartViewSet

cart_list = CartViewSet.as_view({
    'get': 'list',
    'post': 'create',
})

cart_detail = CartViewSet.as_view({
    'delete': 'destroy',
})

urlpatterns = [
    path('', cart_list, name='cart'),
    path('<int:pk>/', cart_detail, name='cart-item'),
]

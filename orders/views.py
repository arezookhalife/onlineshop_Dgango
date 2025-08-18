from rest_framework import viewsets, permissions, status
from rest_framework.response import Response
from .models import Order, OrderItem
from .serializers import OrderSerializer

class OrderViewSet(viewsets.ModelViewSet):
    queryset = Order.objects.all()
    serializer_class = OrderSerializer

    def get_queryset(self):
        user = self.request.user
        if user.is_staff:
            return Order.objects.all()
        return Order.objects.filter(user=user)

    def get_permissions(self):
        if self.action in ['create', 'list', 'retrieve']:
            return [permissions.IsAuthenticated()]
        elif self.action in ['update', 'partial_update', 'destroy']:
            return [permissions.IsAdminUser()]
        return super().get_permissions()

    def perform_create(self, serializer):
        order = serializer.save(user=self.request.user)

        items = self.request.data.get('items', [])
        for item in items:
            from products.models import Product
            product = Product.objects.get(id=item['product'])
            OrderItem.objects.create(
                order=order,
                product=product,
                quantity=item.get('quantity', 1),
                price=product.price
            )

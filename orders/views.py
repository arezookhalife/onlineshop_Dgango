import requests
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from cart.models import Cart, CartItem
from rest_framework import viewsets, permissions
from rest_framework.response import Response
from .models import Order, OrderItem, PaymentSession
from .serializers import OrderSerializer
from django.conf import settings


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


MERCHANT_ID = settings.ZARINPAL_MERCHANT_ID
PAYMENT_REQUEST_URL = settings.ZARINPAL_PAYMENT_REQUEST_URL
PAYMENT_VERIFICATION_URL = settings.ZARINPAL_PAYMENT_VERIFICATION_URL
CALLBACK_URL = settings.ZARINPAL_CALLBACK_URL


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def checkout(request):
    user = request.user
    try:
        cart = Cart.objects.get(user=user)
    except Cart.DoesNotExist:
        return Response({'message': 'Cart is empty'}, status=400)

    cart_items = CartItem.objects.filter(cart=cart)
    if not cart_items.exists():
        return Response({'message': 'Cart is empty'}, status=400)

    total_price = sum(item.product.price * item.quantity for item in cart_items)

    order = Order.objects.create(user=user, status='pending')
    for item in cart_items:
        OrderItem.objects.create(
            order=order,
            product=item.product,
            quantity=item.quantity,
            price=item.product.price
        )

    payment_data = {
        "merchant_id": MERCHANT_ID,
        "amount": int(total_price),
        "callback_url": CALLBACK_URL,
        "description": f"Payment for user {user.username}",
        "metadata": {"email": user.email, "order_id": order.id}
    }

    response = requests.post(PAYMENT_REQUEST_URL, json=payment_data)
    if response.status_code == 200:
        res_data = response.json()
        if res_data.get('Status') == 100:
            authority = res_data['Authority']

            PaymentSession.objects.create(user=user, cart=cart, authority=authority)

            payment_url = f"https://www.zarinpal.com/pg/StartPay/{authority}"
            return Response({'payment_url': payment_url})

    return Response({'message': 'Payment request failed'}, status=500)



@api_view(['GET'])
def payment_callback(request):
    status = request.GET.get('Status')
    authority = request.GET.get('Authority')

    if status == 'OK' and authority:
        try:
            payment_session = PaymentSession.objects.get(authority=authority)
        except PaymentSession.DoesNotExist:
            return Response({'message': 'Payment session not found'}, status=400)

        cart = payment_session.cart
        user = payment_session.user
        cart_items = CartItem.objects.filter(cart=cart)
        total_price = sum(item.product.price * item.quantity for item in cart_items)

        verification_data = {
            "merchant_id": MERCHANT_ID,
            "amount": int(total_price),
            "authority": authority
        }
        res = requests.post(PAYMENT_VERIFICATION_URL, json=verification_data)
        res_data = res.json()
        if res_data.get('Status') == 100:

            order_id = res_data.get('metadata', {}).get('order_id')
            order = Order.objects.get(id=order_id, user=user)
            order.status = 'completed'
            order.save()

            cart_items.delete()
            cart.delete()

            payment_session.delete()

            return Response({'message': 'Payment successful and order completed'})

    return Response({'message': 'Payment failed'}, status=400)
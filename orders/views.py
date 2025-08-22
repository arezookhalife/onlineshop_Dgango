import requests
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from cart.models import Cart, CartItem
from rest_framework import viewsets, permissions
from rest_framework.response import Response
from .models import Order, OrderItem, PaymentSession
from .serializers import OrderSerializer
from django.conf import settings
from users.models import UserInfo
from django.db import transaction
from .permissions import OrderPermission


class OrderViewSet(viewsets.ModelViewSet):
    queryset = Order.objects.all()
    serializer_class = OrderSerializer
    permission_classes = [IsAuthenticated, OrderPermission]

    def get_queryset(self):
        user = self.request.user
        if user.is_staff:
            return Order.objects.all()
        return Order.objects.filter(user=user)

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
CURRENCY = settings.ZARINPAL_CURRENCY
STARTPAY_URL = settings.ZARINPAL_STARTPAY_URL


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def checkout(request):
    user = request.user
    try:
        user_info = user.user_info
    except UserInfo.DoesNotExist:
        return Response(
            {'message': 'User information is required before checkout.'},
            status=400
        )

    required_fields = [user_info.full_name, user_info.phone, user_info.address,
                       user_info.city, user_info.postal_code]
    if not all(required_fields):
        return Response(
            {'message': 'Please complete your profile (name, phone, address, city, postal code).'},
            status=400
        )

    try:
        cart = Cart.objects.get(user=user)
    except Cart.DoesNotExist:
        return Response({'message': 'Cart is empty'}, status=400)

    cart_items = CartItem.objects.filter(cart=cart)
    if not cart_items.exists():
        return Response({'message': 'Cart is empty'}, status=400)

    insufficient_stock = []
    for item in cart_items:
        if item.quantity > item.product.stock:
            insufficient_stock.append({
                'product': item.product.name,
                'available_stock': item.product.stock,
                'requested': item.quantity
            })

    if insufficient_stock:
        return Response({
            'message': 'Some products have insufficient stock',
            'details': insufficient_stock
        }, status=400)

    total_price = sum(item.product.price * item.quantity for item in cart_items)

    order, created = Order.objects.get_or_create(
        user=user,
        status='pending',
        defaults={'total_price': total_price}
    )
    if not created:
        order.total_price = total_price
        order.items.all().delete()
        order.save()

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
        "currency": CURRENCY,
        "description": f"Payment for user {user.username}",
        "metadata": {"email": user.email, "order_id": str(order.id)}
    }

    response = requests.post(PAYMENT_REQUEST_URL, json=payment_data)
    print(response.json())
    if response.status_code == 200:
        res_data = response.json()
        if res_data.get('data') and res_data['data'].get('code') == 100:
            authority = res_data['data']['authority']

            PaymentSession.objects.create(user=user, cart=cart, authority=authority, order=order)

            payment_url = f"{STARTPAY_URL}{authority}"

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

        order = payment_session.order
        cart = payment_session.cart
        cart_items = CartItem.objects.filter(cart=cart)
        total_price = int(payment_session.order.total_price)

        verification_data = {
            "merchant_id": MERCHANT_ID,
            "amount": int(total_price),
            "authority": authority
        }
        res = requests.post(PAYMENT_VERIFICATION_URL, json=verification_data)
        res_data = res.json()

        if not res_data.get("data"):
            return Response({"message": "Invalid payment response"}, status=400)

        code = res_data["data"].get("code")
        if code not in [100, 101]:
            return Response({"message": f"Payment failed with code {code}"}, status=400)

        try:
            with transaction.atomic():
                for item in cart_items:
                    if item.quantity > item.product.stock:
                        return Response({
                            'message': f"Product '{item.product.name}' has insufficient stock"
                        }, status=400)

                for item in cart_items:
                    item.product.stock -= item.quantity
                    item.product.save()

                order.status = 'completed'
                order.save()

                cart_items.delete()
                cart.delete()
                payment_session.delete()

        except Exception as e:
            return Response({'message': f'Error processing order: {str(e)}'}, status=500)

        return Response({'message': 'Payment successful and order completed'})
    return Response({'message': 'Payment failed'}, status=400)
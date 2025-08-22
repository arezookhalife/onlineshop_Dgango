from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework import generics, viewsets, permissions
from .serializers import RegisterSerializer, UserUpdateSerializer, UserInfoSerializer
from django.contrib.auth import get_user_model
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from .models import UserInfo
from .permissions import IsOwner

User = get_user_model()

class RegisterView(generics.CreateAPIView):
    queryset = User.objects.all()
    serializer_class = RegisterSerializer
    permission_classes = [permissions.AllowAny]
    authentication_classes = []

class UserUpdateView(generics.RetrieveUpdateAPIView):
    serializer_class = UserUpdateSerializer
    permission_classes = [permissions.IsAuthenticated]
    authentication_classes = [JWTAuthentication]

    def get_object(self):
        return self.request.user


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def protected_view(request):
    user = request.user
    return Response({"message": f"Hello, {user.username} (id: {user.id})"})

class UserInfoViewSet(viewsets.ModelViewSet):
    serializer_class = UserInfoSerializer
    permission_classes = [IsOwner]

    def get_queryset(self):
        if self.request.user.is_staff or self.request.user.is_superuser:
            return UserInfo.objects.all()
        return UserInfo.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import User, UserInfo

class UserInfoInline(admin.StackedInline):
    model = UserInfo
    can_delete = False
    verbose_name_plural = "User Info"

@admin.register(User)
class UserAdmin(BaseUserAdmin):
    list_display = ("username", "email", "is_staff", "is_superuser", "date_joined")
    search_fields = ("username", "email")
    inlines = [UserInfoInline]

@admin.register(UserInfo)
class UserInfoAdmin(admin.ModelAdmin):
    list_display = ("full_name", "phone", "city", "country", "user")
    search_fields = ("full_name", "phone", "city", "country")
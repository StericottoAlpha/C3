from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import User


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    """カスタムユーザー管理画面"""

    list_display = ['user_id', 'store', 'user_type', 'email', 'is_active', 'created_at']
    list_filter = ['user_type', 'is_active', 'store']
    search_fields = ['user_id', 'email']
    ordering = ['-created_at']

    fieldsets = (
        (None, {'fields': ('user_id', 'password')}),
        ('個人情報', {'fields': ('email', 'store', 'user_type')}),
        ('権限', {'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')}),
        ('重要な日付', {'fields': ('login_at', 'last_access_at', 'created_at')}),
    )

    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('user_id', 'store', 'user_type', 'email', 'password1', 'password2', 'is_active', 'is_staff'),
        }),
    )

    readonly_fields = ['created_at', 'login_at', 'last_access_at']

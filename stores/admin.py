from django.contrib import admin
from .models import Store


@admin.register(Store)
class StoreAdmin(admin.ModelAdmin):
    """店舗管理画面"""

    list_display = ['store_id', 'store_name', 'manager', 'address', 'created_at']
    list_filter = ['created_at']
    search_fields = ['store_name', 'address']
    ordering = ['store_id']

    fieldsets = (
        (None, {'fields': ('store_name', 'manager', 'address', 'sales_target')}),
        ('日付', {'fields': ('created_at',)}),
    )

    readonly_fields = ['created_at']

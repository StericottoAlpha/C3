from django.contrib import admin
from .models import PageVisit


@admin.register(PageVisit)
class PageVisitAdmin(admin.ModelAdmin):
    """ページ訪問管理画面"""

    list_display = ['id', 'message', 'visited_at']
    list_filter = ['visited_at']
    search_fields = ['message']
    ordering = ['-visited_at']

    readonly_fields = ['visited_at']

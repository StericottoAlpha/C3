from django.contrib import admin
from .models import DailyReport, ReportImage, StoreDailyPerformance


class ReportImageInline(admin.TabularInline):
    """日報画像インライン"""
    model = ReportImage
    extra = 1
    readonly_fields = ['uploaded_at']


@admin.register(DailyReport)
class DailyReportAdmin(admin.ModelAdmin):
    """日報管理画面"""

    list_display = ['report_id', 'date', 'store', 'user', 'genre', 'location', 'title', 'post_to_bbs', 'created_at']
    list_filter = ['genre', 'location', 'post_to_bbs', 'store', 'date']
    search_fields = ['title', 'content']
    ordering = ['-date', '-created_at']
    inlines = [ReportImageInline]

    fieldsets = (
        (None, {'fields': ('store', 'user', 'date')}),
        ('日報内容', {'fields': ('genre', 'location', 'title', 'content', 'post_to_bbs')}),
        ('日付', {'fields': ('created_at',)}),
    )

    readonly_fields = ['created_at']


@admin.register(ReportImage)
class ReportImageAdmin(admin.ModelAdmin):
    """日報画像管理画面"""

    list_display = ['image_id', 'report', 'file_path', 'uploaded_at']
    list_filter = ['uploaded_at']
    search_fields = ['report__title']
    ordering = ['-uploaded_at']

    readonly_fields = ['uploaded_at']


@admin.register(StoreDailyPerformance)
class StoreDailyPerformanceAdmin(admin.ModelAdmin):
    """店舗日次実績管理画面"""

    list_display = ['performance_id', 'store', 'date', 'sales_amount', 'customer_count', 'cash_difference', 'registered_by', 'created_at']
    list_filter = ['store', 'date']
    search_fields = ['store__store_name']
    ordering = ['-date']

    fieldsets = (
        (None, {'fields': ('store', 'date')}),
        ('実績データ', {'fields': ('sales_amount', 'customer_count', 'cash_difference')}),
        ('登録情報', {'fields': ('registered_by', 'created_at', 'updated_at')}),
    )

    readonly_fields = ['created_at', 'updated_at']

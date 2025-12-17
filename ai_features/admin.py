from django.contrib import admin
from .models import AIChatHistory

@admin.register(AIChatHistory)
class AIChatHistoryAdmin(admin.ModelAdmin):
    """チャット履歴管理"""

    list_display = ('chat_id', 'user', 'role', 'message_preview', 'created_at')
    list_filter = ('role', 'created_at', 'user__store')
    search_fields = ('message', 'user__user_id', 'user__email')
    readonly_fields = ('chat_id', 'created_at')
    ordering = ('-created_at',)

    def message_preview(self, obj):
        """メッセージのプレビュー（最初の50文字）"""
        return obj.message[:50] + '...' if len(obj.message) > 50 else obj.message
        
    message_preview.short_description = 'メッセージ'

    fieldsets = (
        ('基本情報', {
            'fields': ('chat_id', 'user', 'role', 'created_at')
            }),
        ('メッセージ内容', {
            'fields': ('message',)
            }),
        )
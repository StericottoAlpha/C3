from django.contrib import admin
from .models import AIProposal, AIAnalysisResult, AIChatHistory


@admin.register(AIProposal)
class AIProposalAdmin(admin.ModelAdmin):
    """AI改善提案管理画面"""

    list_display = ['proposal_id', 'user', 'priority', 'proposal_type', 'is_read', 'created_at']
    list_filter = ['priority', 'proposal_type', 'is_read', 'created_at']
    search_fields = ['content', 'user__user_id']
    ordering = ['-priority', '-created_at']

    fieldsets = (
        (None, {'fields': ('user', 'priority', 'proposal_type')}),
        ('提案内容', {'fields': ('content', 'is_read')}),
        ('日付', {'fields': ('created_at',)}),
    )

    readonly_fields = ['created_at']


@admin.register(AIAnalysisResult)
class AIAnalysisResultAdmin(admin.ModelAdmin):
    """AI分析結果管理画面"""

    list_display = ['analysis_id', 'target_period', 'analysis_type', 'created_at']
    list_filter = ['analysis_type', 'created_at']
    search_fields = ['target_period']
    ordering = ['-created_at']

    fieldsets = (
        (None, {'fields': ('target_period', 'analysis_type')}),
        ('分析結果', {'fields': ('analysis_result', 'warning_points')}),
        ('日付', {'fields': ('created_at',)}),
    )

    readonly_fields = ['created_at']


@admin.register(AIChatHistory)
class AIChatHistoryAdmin(admin.ModelAdmin):
    """AIチャット履歴管理画面"""

    list_display = ['chat_id', 'user', 'role', 'message_preview', 'created_at']
    list_filter = ['role', 'created_at']
    search_fields = ['message', 'user__user_id']
    ordering = ['-created_at']

    fieldsets = (
        (None, {'fields': ('user', 'role')}),
        ('メッセージ', {'fields': ('message',)}),
        ('日付', {'fields': ('created_at',)}),
    )

    readonly_fields = ['created_at']

    def message_preview(self, obj):
        """メッセージのプレビュー表示"""
        return obj.message[:50] + '...' if len(obj.message) > 50 else obj.message
    message_preview.short_description = 'メッセージプレビュー'

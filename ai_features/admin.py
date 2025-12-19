from django.contrib import admin
from .models import AIChatHistory, DocumentVector, KnowledgeVector

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


@admin.register(DocumentVector)
class DocumentVectorAdmin(admin.ModelAdmin):
    """ドキュメントベクトル管理"""

    list_display = ('vector_id', 'source_type', 'source_id', 'content_preview', 'created_at')
    list_filter = ('source_type', 'created_at')
    search_fields = ('content', 'metadata')
    readonly_fields = ('vector_id', 'created_at', 'updated_at')
    ordering = ('-created_at',)

    def content_preview(self, obj):
        """コンテンツのプレビュー（最初の50文字）"""
        return obj.content[:50] + '...' if len(obj.content) > 50 else obj.content

    content_preview.short_description = 'コンテンツ'

    fieldsets = (
        ('基本情報', {
            'fields': ('vector_id', 'source_type', 'source_id', 'created_at', 'updated_at')
            }),
        ('コンテンツ', {
            'fields': ('content', 'metadata')
            }),
        ('ベクトル', {
            'fields': ('embedding',),
            'classes': ('collapse',)
            }),
        )


@admin.register(KnowledgeVector)
class KnowledgeVectorAdmin(admin.ModelAdmin):
    """ナレッジベクトル管理"""

    list_display = ('vector_id', 'document_type', 'title', 'content_preview', 'created_at')
    list_filter = ('document_type', 'created_at')
    search_fields = ('title', 'content', 'metadata')
    readonly_fields = ('vector_id', 'created_at', 'updated_at')
    ordering = ('-created_at',)

    def content_preview(self, obj):
        """コンテンツのプレビュー（最初の50文字）"""
        return obj.content[:50] + '...' if len(obj.content) > 50 else obj.content

    content_preview.short_description = 'コンテンツ'

    fieldsets = (
        ('基本情報', {
            'fields': ('vector_id', 'document_type', 'title', 'created_at', 'updated_at')
            }),
        ('コンテンツ', {
            'fields': ('content', 'metadata')
            }),
        ('ベクトル', {
            'fields': ('embedding',),
            'classes': ('collapse',)
            }),
        )
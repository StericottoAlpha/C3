from django.contrib import admin
from .models import BBSPost, BBSReaction, BBSComment


class BBSCommentInline(admin.TabularInline):
    """掲示板コメントインライン"""
    model = BBSComment
    extra = 1
    readonly_fields = ['created_at', 'updated_at']


class BBSReactionInline(admin.TabularInline):
    """掲示板リアクションインライン"""
    model = BBSReaction
    extra = 0
    readonly_fields = ['created_at']


@admin.register(BBSPost)
class BBSPostAdmin(admin.ModelAdmin):
    """掲示板投稿管理画面"""

    list_display = ['post_id', 'store', 'user', 'title', 'comment_count', 'created_at', 'updated_at']
    list_filter = ['store', 'created_at']
    search_fields = ['title', 'content', 'user__user_id']
    ordering = ['-created_at']
    inlines = [BBSCommentInline, BBSReactionInline]

    fieldsets = (
        (None, {'fields': ('store', 'user', 'report')}),
        ('投稿内容', {'fields': ('title', 'content', 'comment_count')}),
        ('日付', {'fields': ('created_at', 'updated_at')}),
    )

    readonly_fields = ['created_at', 'updated_at']


@admin.register(BBSReaction)
class BBSReactionAdmin(admin.ModelAdmin):
    """掲示板リアクション管理画面"""

    list_display = ['reaction_id', 'post', 'user', 'reaction_type', 'created_at']
    list_filter = ['reaction_type', 'created_at']
    search_fields = ['post__title', 'user__user_id']
    ordering = ['-created_at']

    readonly_fields = ['created_at']


@admin.register(BBSComment)
class BBSCommentAdmin(admin.ModelAdmin):
    """掲示板コメント管理画面"""

    list_display = ['comment_id', 'post', 'user', 'is_best_answer', 'created_at', 'updated_at']
    list_filter = ['is_best_answer', 'created_at']
    search_fields = ['content', 'post__title', 'user__user_id']
    ordering = ['-created_at']

    fieldsets = (
        (None, {'fields': ('post', 'user')}),
        ('コメント内容', {'fields': ('content', 'is_best_answer')}),
        ('日付', {'fields': ('created_at', 'updated_at')}),
    )

    readonly_fields = ['created_at', 'updated_at']

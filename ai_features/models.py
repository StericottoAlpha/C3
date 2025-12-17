from django.db import models
from django.conf import settings
from pgvector.django import VectorField

class AIChatHistory(models.Model):
    """AIチャット履歴モデル"""

    ROLE_CHOICES = [
        ('user', 'ユーザー'),
        ('assistant', 'AI'),
    ]

    chat_id = models.AutoField(primary_key=True, verbose_name='チャットID')
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='ai_chats',
        verbose_name='ユーザーID'
    )
    role = models.CharField(
        max_length=20,
        choices=ROLE_CHOICES,
        verbose_name='役割'
    )
    message = models.TextField(verbose_name='メッセージ')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='作成日時')

    class Meta:
        db_table = 'ai_chat_history'
        verbose_name = 'AIチャット履歴'
        verbose_name_plural = 'AIチャット履歴'
        ordering = ['created_at']

    def __str__(self):
        return f"{self.user} - {self.get_role_display()} - {self.created_at}"


class DocumentVector(models.Model):
    """ドキュメントベクトルモデル（実績RAG用）"""

    SOURCE_TYPE_CHOICES = [
        ('daily_report', '日報'),
        ('bbs_post', '掲示板投稿'),
        ('bbs_comment', '掲示板コメント'),
        ('performance', '店舗実績'),
    ]

    vector_id = models.AutoField(primary_key=True, verbose_name='ベクトルID')
    source_type = models.CharField(
        max_length=20,
        choices=SOURCE_TYPE_CHOICES,
        verbose_name='ソース種別',
        db_index=True
    )
    source_id = models.IntegerField(verbose_name='ソースID', db_index=True)
    content = models.TextField(verbose_name='コンテンツ')
    metadata = models.JSONField(
        default=dict,
        verbose_name='メタデータ',
        help_text='store_id, date, title などの追加情報'
    )
    embedding = VectorField(
        dimensions=384,
        verbose_name='埋め込みベクトル'
    )
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='作成日時', db_index=True)
    updated_at = models.DateTimeField(auto_now=True, verbose_name='更新日時')

    class Meta:
        db_table = 'document_vectors'
        verbose_name = 'ドキュメントベクトル'
        verbose_name_plural = 'ドキュメントベクトル'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['source_type', 'source_id']),
            models.Index(fields=['created_at']),
        ]
        unique_together = [['source_type', 'source_id']]

    def __str__(self):
        return f"{self.get_source_type_display()} - ID:{self.source_id}"
from django.db import models
from django.conf import settings
from pgvector.django import VectorField


class AIProposal(models.Model):
    """AI改善提案モデル"""

    PRIORITY_CHOICES = [
        (1, '低'),
        (2, '中'),
        (3, '高'),
    ]

    PROPOSAL_TYPE_CHOICES = [
        ('frequent_claim', '頻発するクレーム'),
        ('performance_decline', '自己評価の低下'),
        ('cash_difference', '違算の基準値超過'),
        ('other', 'その他'),
    ]

    proposal_id = models.AutoField(primary_key=True, verbose_name='提案ID')
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='ai_proposals',
        verbose_name='ユーザーID'
    )
    priority = models.IntegerField(
        choices=PRIORITY_CHOICES,
        default=2,
        verbose_name='優先度'
    )
    proposal_type = models.CharField(
        max_length=50,
        choices=PROPOSAL_TYPE_CHOICES,
        verbose_name='種類'
    )
    content = models.TextField(verbose_name='提案内容')
    is_read = models.BooleanField(default=False, verbose_name='既読')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='作成日時')

    class Meta:
        db_table = 'ai_proposals'
        verbose_name = 'AI改善提案'
        verbose_name_plural = 'AI改善提案'
        ordering = ['-priority', '-created_at']

    def __str__(self):
        return f"{self.get_proposal_type_display()} - {self.user}"


class AIAnalysisResult(models.Model):
    """AI分析結果モデル"""

    ANALYSIS_TYPE_CHOICES = [
        ('daily', '日次分析'),
        ('weekly', '週次分析'),
        ('monthly', '月次分析'),
        ('custom', 'カスタム分析'),
    ]

    analysis_id = models.AutoField(primary_key=True, verbose_name='解析ID')
    target_period = models.CharField(max_length=100, verbose_name='対象期間')
    analysis_type = models.CharField(
        max_length=20,
        choices=ANALYSIS_TYPE_CHOICES,
        verbose_name='解析種別'
    )
    analysis_result = models.JSONField(verbose_name='解析結果')  # 分析結果の詳細データ
    warning_points = models.JSONField(verbose_name='以上箇所')  # 問題点のリスト
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='作成日時')

    class Meta:
        db_table = 'ai_analysis_results'
        verbose_name = 'AI分析結果'
        verbose_name_plural = 'AI分析結果'
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.get_analysis_type_display()} - {self.target_period}"


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
        help_text='store_id, user_id, date, title などの追加情報'
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


class KnowledgeDocument(models.Model):
    """業務マニュアル・規則の原本管理モデル"""

    DOCUMENT_TYPE_CHOICES = [
        ('manual', 'マニュアル'),
        ('guideline', 'ガイドライン'),
        ('faq', 'FAQ'),
        ('policy', 'ポリシー'),
    ]

    CATEGORY_CHOICES = [
        ('hygiene', '衛生管理'),
        ('service', '接客'),
        ('cooking', '調理'),
        ('safety', '安全管理'),
        ('other', 'その他'),
    ]

    FILE_TYPE_CHOICES = [
        ('pdf', 'PDF'),
        ('docx', 'Word'),
        ('md', 'Markdown'),
    ]

    document_id = models.AutoField(primary_key=True, verbose_name='ドキュメントID')
    document_type = models.CharField(
        max_length=20,
        choices=DOCUMENT_TYPE_CHOICES,
        verbose_name='ドキュメント種別'
    )
    title = models.CharField(max_length=200, verbose_name='タイトル')
    category = models.CharField(
        max_length=20,
        choices=CATEGORY_CHOICES,
        verbose_name='カテゴリ'
    )

    # ファイル情報
    file_path = models.FileField(
        upload_to='knowledge/',
        verbose_name='ファイルパス'
    )
    file_type = models.CharField(
        max_length=10,
        choices=FILE_TYPE_CHOICES,
        verbose_name='ファイル種別'
    )

    # バージョン管理
    version = models.CharField(max_length=50, verbose_name='バージョン')
    is_active = models.BooleanField(default=True, verbose_name='有効')

    # メタデータ
    description = models.TextField(blank=True, verbose_name='説明')
    author = models.CharField(max_length=100, blank=True, verbose_name='作成者')
    published_date = models.DateField(null=True, blank=True, verbose_name='公開日')

    # ベクトル化状態
    vectorized = models.BooleanField(default=False, verbose_name='ベクトル化済み')
    vectorized_at = models.DateTimeField(null=True, blank=True, verbose_name='ベクトル化日時')

    created_at = models.DateTimeField(auto_now_add=True, verbose_name='作成日時')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='更新日時')

    class Meta:
        db_table = 'knowledge_documents'
        verbose_name = 'ナレッジドキュメント'
        verbose_name_plural = 'ナレッジドキュメント'
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.title} (v{self.version})"


class KnowledgeVector(models.Model):
    """業務マニュアル・規則のベクトル表現モデル（ナレッジRAG用）"""

    DOCUMENT_TYPE_CHOICES = [
        ('manual', 'マニュアル'),
        ('guideline', 'ガイドライン'),
        ('faq', 'FAQ'),
        ('policy', 'ポリシー'),
    ]

    CATEGORY_CHOICES = [
        ('hygiene', '衛生管理'),
        ('service', '接客'),
        ('cooking', '調理'),
        ('safety', '安全管理'),
        ('other', 'その他'),
    ]

    vector_id = models.AutoField(primary_key=True, verbose_name='ベクトルID')

    # ドキュメント情報
    document = models.ForeignKey(
        KnowledgeDocument,
        on_delete=models.CASCADE,
        related_name='vectors',
        verbose_name='元ドキュメント'
    )
    document_type = models.CharField(
        max_length=20,
        choices=DOCUMENT_TYPE_CHOICES,
        verbose_name='ドキュメント種別',
        db_index=True
    )

    # コンテンツ
    content = models.TextField(verbose_name='チャンクコンテンツ')

    # メタデータ
    metadata = models.JSONField(
        default=dict,
        verbose_name='メタデータ',
        help_text='category, document_title, chapter, section, version などの情報'
    )

    # ベクトル
    embedding = VectorField(
        dimensions=384,
        verbose_name='埋め込みベクトル'
    )

    created_at = models.DateTimeField(auto_now_add=True, verbose_name='作成日時', db_index=True)
    updated_at = models.DateTimeField(auto_now=True, verbose_name='更新日時')

    class Meta:
        db_table = 'knowledge_vectors'
        verbose_name = 'ナレッジベクトル'
        verbose_name_plural = 'ナレッジベクトル'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['document_type']),
            models.Index(fields=['created_at']),
        ]

    def __str__(self):
        return f"{self.get_document_type_display()} - {self.document.title} (Chunk ID:{self.vector_id})"

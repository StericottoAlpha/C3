from django.db import models
from django.conf import settings


# class AIProposal(models.Model):
#     """AI改善提案モデル"""

#     PRIORITY_CHOICES = [
#         (1, '低'),
#         (2, '中'),
#         (3, '高'),
#     ]

#     PROPOSAL_TYPE_CHOICES = [
#         ('frequent_claim', '頻発するクレーム'),
#         ('performance_decline', '自己評価の低下'),
#         ('cash_difference', '違算の基準値超過'),
#         ('other', 'その他'),
#     ]

#     proposal_id = models.AutoField(primary_key=True, verbose_name='提案ID')
#     user = models.ForeignKey(
#         settings.AUTH_USER_MODEL,
#         on_delete=models.CASCADE,
#         related_name='ai_proposals',
#         verbose_name='ユーザーID'
#     )
#     priority = models.IntegerField(
#         choices=PRIORITY_CHOICES,
#         default=2,
#         verbose_name='優先度'
#     )
#     proposal_type = models.CharField(
#         max_length=50,
#         choices=PROPOSAL_TYPE_CHOICES,
#         verbose_name='種類'
#     )
#     content = models.TextField(verbose_name='提案内容')
#     is_read = models.BooleanField(default=False, verbose_name='既読')
#     created_at = models.DateTimeField(auto_now_add=True, verbose_name='作成日時')

#     class Meta:
#         db_table = 'ai_proposals'
#         verbose_name = 'AI改善提案'
#         verbose_name_plural = 'AI改善提案'
#         ordering = ['-priority', '-created_at']

#     def __str__(self):
#         return f"{self.get_proposal_type_display()} - {self.user}"


# class AIAnalysisResult(models.Model):
#     """AI分析結果モデル"""

#     ANALYSIS_TYPE_CHOICES = [
#         ('daily', '日次分析'),
#         ('weekly', '週次分析'),
#         ('monthly', '月次分析'),
#         ('custom', 'カスタム分析'),
#     ]

#     analysis_id = models.AutoField(primary_key=True, verbose_name='解析ID')
#     target_period = models.CharField(max_length=100, verbose_name='対象期間')
#     analysis_type = models.CharField(
#         max_length=20,
#         choices=ANALYSIS_TYPE_CHOICES,
#         verbose_name='解析種別'
#     )
#     analysis_result = models.JSONField(verbose_name='解析結果')  # 分析結果の詳細データ
#     warning_points = models.JSONField(verbose_name='以上箇所')  # 問題点のリスト
#     created_at = models.DateTimeField(auto_now_add=True, verbose_name='作成日時')

#     class Meta:
#         db_table = 'ai_analysis_results'
#         verbose_name = 'AI分析結果'
#         verbose_name_plural = 'AI分析結果'
#         ordering = ['-created_at']

#     def __str__(self):
#         return f"{self.get_analysis_type_display()} - {self.target_period}"


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


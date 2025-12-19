from django.db import models
from django.conf import settings


class BBSPost(models.Model):
    """掲示板投稿モデル"""

    post_id = models.AutoField(primary_key=True, verbose_name='投稿ID')
    store = models.ForeignKey(
        'stores.Store',
        on_delete=models.CASCADE,
        related_name='bbs_posts',
        verbose_name='店舗ID'
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='bbs_posts',
        verbose_name='ユーザーID'
    )
    report = models.ForeignKey(
        'reports.DailyReport',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='bbs_post',
        verbose_name='日報ID'
    )
    title = models.CharField(max_length=200, verbose_name='タイトル')
    content = models.TextField(verbose_name='本文')
    comment_count = models.IntegerField(default=0, verbose_name='コメント数')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='投稿日時')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='更新日時')

    class Meta:
        db_table = 'bbs_posts'
        verbose_name = '掲示板投稿'
        verbose_name_plural = '掲示板投稿'
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.title} - {self.user}"


class BBSReaction(models.Model):
    """掲示板リアクションモデル（投稿へのリアクション）"""

    REACTION_CHOICES = [
        ('naruhodo', 'なるほど'),
        ('iine', 'いいね'),
    ]

    reaction_id = models.AutoField(primary_key=True, verbose_name='リアクションID')
    post = models.ForeignKey(
        BBSPost,
        on_delete=models.CASCADE,
        related_name='reactions',
        verbose_name='投稿ID'
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='reactions',
        verbose_name='ユーザーID'
    )
    reaction_type = models.CharField(
        max_length=20,
        choices=REACTION_CHOICES,
        verbose_name='リアクション種別'
    )
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='作成日時')

    class Meta:
        db_table = 'bbs_reactions'
        verbose_name = '掲示板リアクション'
        verbose_name_plural = '掲示板リアクション'
        unique_together = [['post', 'user', 'reaction_type']]  # 1ユーザーは同じ投稿に同じリアクションは1回のみ

    def __str__(self):
        return f"{self.user} - {self.get_reaction_type_display()}"


class BBSComment(models.Model):
    """掲示板コメントモデル"""

    comment_id = models.AutoField(primary_key=True, verbose_name='コメントID')
    post = models.ForeignKey(
        BBSPost,
        on_delete=models.CASCADE,
        related_name='comments',
        verbose_name='投稿ID'
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='comments',
        verbose_name='ユーザーID'
    )
    content = models.TextField(verbose_name='本文')
    is_best_answer = models.BooleanField(default=False, verbose_name='ベストアンサーフラグ')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='投稿日時')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='更新日時')

    class Meta:
        db_table = 'bbs_comments'
        verbose_name = '掲示板コメント'
        verbose_name_plural = '掲示板コメント'
        ordering = ['created_at']

    def __str__(self):
        return f"Comment by {self.user} on {self.post.title}"


# 【追加】コメントへのリアクションモデル
class BBSCommentReaction(models.Model):
    """掲示板コメントリアクションモデル"""

    # 投稿用と同じ選択肢を使用（必要に応じて変更可）
    REACTION_CHOICES = [
        ('naruhodo', 'なるほど'),
        ('iine', 'いいね'),
    ]

    reaction_id = models.AutoField(primary_key=True, verbose_name='リアクションID')
    comment = models.ForeignKey(
        BBSComment,
        on_delete=models.CASCADE,
        related_name='reactions', # viewで使う related_name='reactions' と一致させる
        verbose_name='コメントID'
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='comment_reactions',
        verbose_name='ユーザーID'
    )
    reaction_type = models.CharField(
        max_length=20,
        choices=REACTION_CHOICES,
        verbose_name='リアクション種別'
    )
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='作成日時')

    class Meta:
        db_table = 'bbs_comment_reactions'
        verbose_name = '掲示板コメントリアクション'
        verbose_name_plural = '掲示板コメントリアクション'
        unique_together = [['comment', 'user', 'reaction_type']]
    def __str__(self):
        return f"{self.user} - {self.get_reaction_type_display()} (Comment)"
from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()


class Store(models.Model):
    """店舗モデル"""
    store_id = models.AutoField(primary_key=True, verbose_name='店舗ID')
    manager = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='managed_stores',
        verbose_name='管理者ユーザーID'
    )
    store_name = models.CharField(max_length=100, verbose_name='店舗名')
    address = models.CharField(max_length=255, verbose_name='住所')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='作成日時')

    class Meta:
        db_table = 'stores'
        verbose_name = '店舗'
        verbose_name_plural = '店舗'

    def __str__(self):
        return f"{self.store_name}"


class MonthlyGoal(models.Model):
    """月次目標モデル"""

    goal_id = models.AutoField(primary_key=True, verbose_name='目標ID')
    store = models.ForeignKey(
        Store,
        on_delete=models.CASCADE,
        related_name='monthly_goals',
        verbose_name='店舗ID'
    )
    year = models.IntegerField(verbose_name='年')
    month = models.IntegerField(verbose_name='月')
    goal_text = models.TextField(verbose_name='目標内容')
    achievement_rate = models.IntegerField(default=0, verbose_name='達成率（%）')
    achievement_text = models.TextField(blank=True, verbose_name='達成状況')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='作成日時')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='更新日時')

    class Meta:
        db_table = 'monthly_goals'
        verbose_name = '月次目標'
        verbose_name_plural = '月次目標'
        ordering = ['-year', '-month']
        unique_together = [['store', 'year', 'month']]  # 1店舗1月1レコード

    def __str__(self):
        return f"{self.store.store_name} - {self.year}年{self.month}月"

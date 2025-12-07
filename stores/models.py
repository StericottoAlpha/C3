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
    sales_target = models.CharField(max_length=255, blank=True, verbose_name='売り上げ目標')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='作成日時')

    class Meta:
        db_table = 'stores'
        verbose_name = '店舗'
        verbose_name_plural = '店舗'

    def __str__(self):
        return f"{self.store_name}"

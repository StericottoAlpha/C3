from django.db import models
from django.conf import settings


def report_image_upload_path(instance, filename):
    """日報画像のアップロードパスを生成"""
    store_id = instance.report.store_id
    date = instance.report.date
    return f'reports/store_{store_id}/{date.year}/{date.month:02d}/{date.day:02d}/{filename}'


class DailyReport(models.Model):
    """日報モデル"""

    GENRE_CHOICES = [
        ('claim', 'クレーム'),
        ('praise', '賞賛'),
        ('accident', '事故'),
        ('report', '報告'),
        ('other', 'その他'),
    ]

    LOCATION_CHOICES = [
        ('kitchen', 'キッチン'),
        ('hall', 'ホール'),
        ('cashier', 'レジ'),
        ('toilet', 'トイレ'),
        ('other', 'その他'),
    ]

    report_id = models.AutoField(primary_key=True, verbose_name='日報ID')
    store = models.ForeignKey(
        'stores.Store',
        on_delete=models.CASCADE,
        related_name='reports',
        verbose_name='店舗ID'
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name='reports',
        verbose_name='ユーザーID'
    )
    date = models.DateField(verbose_name='日時')
    genre = models.CharField(
        max_length=20,
        choices=GENRE_CHOICES,
        verbose_name='ジャンル'
    )
    location = models.CharField(
        max_length=20,
        choices=LOCATION_CHOICES,
        verbose_name='場所'
    )
    title = models.CharField(max_length=200, verbose_name='件名')
    content = models.TextField(verbose_name='内容')
    post_to_bbs = models.BooleanField(default=False, verbose_name='掲示板連携フラグ')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='作成日時')

    class Meta:
        db_table = 'daily_reports'
        verbose_name = '日報'
        verbose_name_plural = '日報'
        ordering = ['-date', '-created_at']

    def __str__(self):
        return f"{self.date} - {self.title}"


class ReportImage(models.Model):
    """日報画像モデル"""

    image_id = models.AutoField(primary_key=True, verbose_name='画像ID')
    report = models.ForeignKey(
        DailyReport,
        on_delete=models.CASCADE,
        related_name='images',
        verbose_name='日報ID'
    )
    file_path = models.ImageField(
        upload_to=report_image_upload_path,
        verbose_name='ファイルパス'
    )
    uploaded_at = models.DateTimeField(auto_now_add=True, verbose_name='アップロード日時')

    class Meta:
        db_table = 'report_images'
        verbose_name = '日報画像'
        verbose_name_plural = '日報画像'

    def __str__(self):
        return f"Image for {self.report.title}"


class StoreDailyPerformance(models.Model):
    """店舗日次実績モデル（管理者専用）"""

    performance_id = models.AutoField(primary_key=True, verbose_name='実績ID')
    store = models.ForeignKey(
        'stores.Store',
        on_delete=models.CASCADE,
        related_name='daily_performances',
        verbose_name='店舗ID'
    )
    date = models.DateField(verbose_name='日付')
    sales_amount = models.IntegerField(verbose_name='売上金額')
    customer_count = models.IntegerField(verbose_name='客数')
    cash_difference = models.IntegerField(default=0, verbose_name='違算金額')
    registered_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name='registered_performances',
        verbose_name='登録者ユーザーID'
    )
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='作成日時')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='更新日時')

    class Meta:
        db_table = 'store_daily_performances'
        verbose_name = '店舗日次実績'
        verbose_name_plural = '店舗日次実績'
        ordering = ['-date']
        unique_together = [['store', 'date']]  # 1店舗1日1レコード

    def __str__(self):
        return f"{self.store.store_name} - {self.date}"

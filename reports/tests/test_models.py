from django.test import TestCase
from django.contrib.auth import get_user_model
from django.db.utils import IntegrityError
from django.utils import timezone
from stores.models import Store
from reports.models import DailyReport, StoreDailyPerformance, ReportImage

User = get_user_model()

class ReportModelTests(TestCase):
    def setUp(self):
        self.store = Store.objects.create(
            store_name="テスト店舗",
            store_id=1
        )
        self.user = User.objects.create_user(
            user_id="testuser",
            password="password",
            store=self.store
        )
        self.today = timezone.now().date()

    def test_daily_report_str(self):
        """日報モデルの__str__メソッドテスト"""
        report = DailyReport.objects.create(
            store=self.store,
            user=self.user,
            date=self.today,
            genre='claim',
            location='kitchen',
            title='テストタイトル',
            content='テスト内容'
        )
        # __str__ が "日付 - タイトル" の形式か確認
        self.assertEqual(str(report), f"{self.today} - テストタイトル")

    def test_store_daily_performance_unique_constraint(self):
        """店舗日次実績のユニーク制約（同じ店舗・日付で重複登録できない）テスト"""
        # 1つ目を作成
        StoreDailyPerformance.objects.create(
            store=self.store,
            date=self.today,
            sales_amount=10000,
            customer_count=10
        )
        
        # 同じ条件で2つ目を作成しようとするとエラーになるはず
        with self.assertRaises(IntegrityError):
            StoreDailyPerformance.objects.create(
                store=self.store,
                date=self.today, # 同じ日付
                sales_amount=20000,
                customer_count=20
            )

    def test_report_image_creation(self):
        """画像モデルの関連付けテスト"""
        report = DailyReport.objects.create(
            store=self.store,
            user=self.user,
            date=self.today,
            genre='report',
            location='hall',
            title='画像ありレポート',
            content='内容'
        )
        image = ReportImage.objects.create(
            report=report,
            file_path='path/to/image.jpg'
        )
        self.assertEqual(image.report, report)
from django.test import TestCase
from django.contrib.auth import get_user_model
from django.utils import timezone
from unittest.mock import patch, MagicMock
from stores.models import Store
from reports.models import DailyReport
from reports.services import DailyReportService

User = get_user_model()

class DailyReportServiceTests(TestCase):
    def setUp(self):
        self.store = Store.objects.create(store_name="サービス店舗", store_id=10)
        self.user = User.objects.create_user(
            user_id="service_user",
            password="password",
            store=self.store
        )
        self.today = timezone.now().date()

    # AI機能をモック化（実際にAIを動かさない）
    @patch('ai_features.services.core_services.VectorizationService.vectorize_daily_report')
    def test_create_report_service(self, mock_vectorize):
        """日報作成サービス：DB保存とベクトル化呼び出しの確認"""
        
        # モックの返り値を設定
        mock_vectorize.return_value = True

        report = DailyReportService.create_report(
            store=self.store,
            user=self.user,
            date=self.today,
            genre='praise',
            location='hall',
            title='サービス経由作成',
            content='内容',
            post_to_bbs=True
        )

        # DBに保存されたか
        self.assertEqual(DailyReport.objects.count(), 1)
        self.assertEqual(report.title, 'サービス経由作成')
        self.assertTrue(report.post_to_bbs)

        # ベクトル化処理が1回呼ばれたか確認
        mock_vectorize.assert_called_once_with(report.report_id)

    @patch('ai_features.services.core_services.VectorizationService.vectorize_daily_report')
    def test_update_report_service(self, mock_vectorize):
        """日報更新サービス：フィールド更新と再ベクトル化の確認"""
        
        # 事前に日報を作成
        report = DailyReport.objects.create(
            store=self.store,
            user=self.user,
            date=self.today,
            genre='claim',
            location='kitchen',
            title='更新前',
            content='更新前'
        )

        update_fields = {
            'title': '更新後タイトル',
            'content': '更新後内容'
        }

        # 更新サービス実行
        updated_report = DailyReportService.update_report(report, update_fields)

        # 値が変わっているか
        self.assertEqual(updated_report.title, '更新後タイトル')
        self.assertEqual(updated_report.content, '更新後内容')

        # ベクトル化処理が呼ばれたか
        mock_vectorize.assert_called_with(report.report_id)
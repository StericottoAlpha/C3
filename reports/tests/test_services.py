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

    @patch('ai_features.services.core_services.VectorizationService.vectorize_daily_report')
    def test_create_report_vectorization_failure(self, mock_vectorize):
        """ベクトル化が失敗しても日報作成は成功することを確認"""
        # ベクトル化でエラーを発生させる
        mock_vectorize.side_effect = Exception("AI Service Down")

        report = DailyReportService.create_report(
            store=self.store,
            user=self.user,
            date=self.today,
            genre='accident',
            location='toilet',
            title='エラー耐性テスト',
            content='ベクトル化失敗しても保存される',
            post_to_bbs=False
        )

        # 日報は作成されている
        self.assertEqual(DailyReport.objects.count(), 1)
        self.assertEqual(report.title, 'エラー耐性テスト')

    @patch('ai_features.services.core_services.VectorizationService.vectorize_daily_report')
    def test_create_report_vectorization_returns_false(self, mock_vectorize):
        """ベクトル化がFalseを返しても日報作成は成功することを確認"""
        mock_vectorize.return_value = False

        report = DailyReportService.create_report(
            store=self.store,
            user=self.user,
            date=self.today,
            genre='other',
            location='other',
            title='ベクトル化失敗テスト',
            content='内容',
            post_to_bbs=False
        )

        # 日報は作成されている
        self.assertEqual(DailyReport.objects.count(), 1)
        mock_vectorize.assert_called_once()

    @patch('ai_features.services.core_services.VectorizationService.vectorize_daily_report')
    def test_update_report_vectorization_failure(self, mock_vectorize):
        """ベクトル化が失敗しても日報更新は成功することを確認"""
        report = DailyReport.objects.create(
            store=self.store,
            user=self.user,
            date=self.today,
            genre='report',
            location='hall',
            title='元のタイトル',
            content='元の内容'
        )

        # ベクトル化失敗をシミュレート
        mock_vectorize.side_effect = Exception("AI Service Down")

        update_fields = {'title': '更新されたタイトル', 'content': '更新された内容'}
        updated_report = DailyReportService.update_report(report, update_fields)

        # 日報は更新されている
        report.refresh_from_db()
        self.assertEqual(report.title, '更新されたタイトル')
        self.assertEqual(report.content, '更新された内容')

    @patch('ai_features.services.core_services.VectorizationService.vectorize_daily_report')
    def test_update_report_vectorization_returns_false(self, mock_vectorize):
        """ベクトル化がFalseを返しても日報更新は成功することを確認"""
        report = DailyReport.objects.create(
            store=self.store,
            user=self.user,
            date=self.today,
            genre='claim',
            location='kitchen',
            title='元のタイトル',
            content='元の内容'
        )

        mock_vectorize.return_value = False

        update_fields = {'genre': 'praise'}
        updated_report = DailyReportService.update_report(report, update_fields)

        # 日報は更新されている
        report.refresh_from_db()
        self.assertEqual(report.genre, 'praise')

    @patch('ai_features.services.core_services.VectorizationService.vectorize_daily_report')
    def test_revectorize_report_success(self, mock_vectorize):
        """日報の再ベクトル化が成功することを確認"""
        mock_vectorize.return_value = True

        report = DailyReport.objects.create(
            store=self.store,
            user=self.user,
            date=self.today,
            genre='report',
            location='hall',
            title='日報',
            content='内容'
        )

        result = DailyReportService.revectorize_report(report.report_id)

        self.assertTrue(result)
        mock_vectorize.assert_called_once_with(report.report_id)

    @patch('ai_features.services.core_services.VectorizationService.vectorize_daily_report')
    def test_revectorize_report_failure(self, mock_vectorize):
        """日報の再ベクトル化が失敗した場合Falseを返すことを確認"""
        mock_vectorize.return_value = False

        report = DailyReport.objects.create(
            store=self.store,
            user=self.user,
            date=self.today,
            genre='report',
            location='hall',
            title='日報',
            content='内容'
        )

        result = DailyReportService.revectorize_report(report.report_id)

        self.assertFalse(result)

    @patch('ai_features.services.core_services.VectorizationService.vectorize_daily_report')
    def test_revectorize_report_exception(self, mock_vectorize):
        """日報の再ベクトル化でエラーが発生した場合Falseを返すことを確認"""
        mock_vectorize.side_effect = Exception("Vectorization error")

        report = DailyReport.objects.create(
            store=self.store,
            user=self.user,
            date=self.today,
            genre='report',
            location='hall',
            title='日報',
            content='内容'
        )

        result = DailyReportService.revectorize_report(report.report_id)

        self.assertFalse(result)
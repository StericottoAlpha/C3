from django.test import TestCase, Client
from django.contrib.auth import get_user_model
from django.urls import reverse
from django.core.files.uploadedfile import SimpleUploadedFile
from unittest.mock import patch
from datetime import date
from stores.models import Store
from reports.models import DailyReport, ReportImage
from bbs.models import BBSPost

User = get_user_model()


class ReportRegisterViewTest(TestCase):
    """日報登録ビューのテスト"""

    def setUp(self):
        """テスト用データを作成"""
        self.client = Client()
        self.store = Store.objects.create(
            store_name='テスト店舗',
            address='テスト住所'
        )
        self.user = User.objects.create_user(
            user_id='testuser',
            password='testpass123',
            store=self.store
        )
        self.url = reverse('reports:register')

    def test_get_report_register_not_logged_in(self):
        """ログインなしでアクセスするとログインページにリダイレクトされることを確認"""
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 302)
        self.assertIn('/login/', response.url)

    def test_get_report_register_logged_in(self):
        """ログイン済みでアクセスするとフォームが表示されることを確認"""
        self.client.login(user_id='testuser', password='testpass123')
        response = self.client.get(self.url)

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'reports/register.html')
        self.assertIn('form', response.context)

    @patch('ai_features.services.core_services.VectorizationService.vectorize_daily_report')
    def test_post_report_register_valid_data(self, mock_vectorize):
        """有効なデータでPOSTすると日報が作成されることを確認"""
        mock_vectorize.return_value = True

        self.client.login(user_id='testuser', password='testpass123')

        data = {
            'genre': 'report',
            'location': 'hall',
            'title': 'テスト日報',
            'content': '日報の内容',
            'post_to_bbs': False
        }

        response = self.client.post(self.url, data)

        # リダイレクトされることを確認
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, reverse('common:index'))

        # 日報が作成されたことを確認
        self.assertEqual(DailyReport.objects.count(), 1)
        report = DailyReport.objects.first()
        self.assertEqual(report.title, 'テスト日報')
        self.assertEqual(report.genre, 'report')
        self.assertEqual(report.user, self.user)
        self.assertEqual(report.store, self.store)

    @patch('ai_features.services.core_services.VectorizationService.vectorize_daily_report')
    @patch('ai_features.services.core_services.VectorizationService.vectorize_bbs_post')
    def test_post_report_register_with_bbs_post(self, mock_vectorize_bbs, mock_vectorize_report):
        """post_to_bbsがTrueの場合、掲示板投稿も作成されることを確認"""
        mock_vectorize_report.return_value = True
        mock_vectorize_bbs.return_value = True

        self.client.login(user_id='testuser', password='testpass123')

        data = {
            'genre': 'report',
            'location': 'hall',
            'title': 'テスト日報',
            'content': '日報の内容',
            'post_to_bbs': True
        }

        response = self.client.post(self.url, data)

        self.assertEqual(response.status_code, 302)

        # 日報が作成された
        self.assertEqual(DailyReport.objects.count(), 1)

        # 掲示板投稿も作成された
        self.assertEqual(BBSPost.objects.count(), 1)
        bbs_post = BBSPost.objects.first()
        self.assertEqual(bbs_post.title, 'テスト日報')
        self.assertEqual(bbs_post.content, '日報の内容')
        self.assertEqual(bbs_post.user, self.user)
        self.assertEqual(bbs_post.store, self.store)

    @patch('ai_features.services.core_services.VectorizationService.vectorize_daily_report')
    def test_post_report_register_without_bbs(self, mock_vectorize):
        """post_to_bbsがFalseの場合、掲示板投稿は作成されないことを確認"""
        mock_vectorize.return_value = True

        self.client.login(user_id='testuser', password='testpass123')

        data = {
            'genre': 'claim',
            'location': 'kitchen',
            'title': 'BBSなし日報',
            'content': '掲示板には投稿しません',
            'post_to_bbs': False
        }

        response = self.client.post(self.url, data)

        self.assertEqual(response.status_code, 302)
        self.assertEqual(DailyReport.objects.count(), 1)
        # BBSPostは作成されない
        self.assertEqual(BBSPost.objects.count(), 0)

    def test_post_report_register_invalid_data(self):
        """無効なデータでPOSTするとエラーメッセージが表示されることを確認"""
        self.client.login(user_id='testuser', password='testpass123')

        # 必須フィールドが不足しているデータ
        data = {
            'genre': 'report',
            # titleとcontentが欠けている
        }

        response = self.client.post(self.url, data)

        # フォームが再表示される
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'reports/register.html')

        # エラーメッセージが表示される
        messages_list = list(response.context['messages'])
        self.assertEqual(len(messages_list), 1)
        self.assertIn('入力内容に誤りがあります', str(messages_list[0]))

        # 日報は作成されていない
        self.assertEqual(DailyReport.objects.count(), 0)


class ReportViewTest(TestCase):
    """日報詳細ビューのテスト"""

    def setUp(self):
        """テスト用データを作成"""
        self.client = Client()
        self.store = Store.objects.create(
            store_name='テスト店舗',
            address='テスト住所'
        )
        self.user = User.objects.create_user(
            user_id='testuser',
            password='testpass123',
            store=self.store
        )

        # テスト用日報を作成
        self.report = DailyReport.objects.create(
            store=self.store,
            user=self.user,
            date=date(2024, 1, 1),
            genre='report',
            location='hall',
            title='テスト日報',
            content='日報の内容'
        )

    def test_get_report_view_not_logged_in(self):
        """ログインなしでアクセスするとログインページにリダイレクトされることを確認"""
        url = reverse('reports:view', args=[self.report.report_id])
        response = self.client.get(url)

        self.assertEqual(response.status_code, 302)
        self.assertIn('/login/', response.url)

    def test_get_report_view_logged_in(self):
        """ログイン済みでアクセスすると日報が表示されることを確認"""
        self.client.login(user_id='testuser', password='testpass123')
        url = reverse('reports:view', args=[self.report.report_id])
        response = self.client.get(url)

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'reports/view.html')
        self.assertEqual(response.context['report'], self.report)

    def test_get_report_view_nonexistent_report(self):
        """存在しない日報IDでアクセスすると404が返ることを確認"""
        self.client.login(user_id='testuser', password='testpass123')
        url = reverse('reports:view', args=[99999])
        response = self.client.get(url)

        self.assertEqual(response.status_code, 404)

    def test_get_report_view_with_images(self):
        """画像付き日報が正しく表示されることを確認"""
        self.client.login(user_id='testuser', password='testpass123')

        # 画像を追加
        image = SimpleUploadedFile(
            "test_image.jpg",
            b"fake image content",
            content_type="image/jpeg"
        )
        ReportImage.objects.create(
            report=self.report,
            file_path=image
        )

        url = reverse('reports:view', args=[self.report.report_id])
        response = self.client.get(url)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['report'].images.count(), 1)

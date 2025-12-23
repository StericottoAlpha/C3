from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth import get_user_model
from stores.models import Store

User = get_user_model()


class IndexViewTest(TestCase):
    """index()ビューのテスト"""

    def setUp(self):
        """テスト用のユーザーとクライアントを作成"""
        self.client = Client()

        # テスト用の店舗を作成
        self.store = Store.objects.create(
            store_name='テスト店舗',
            address='テスト住所'
        )

        # テスト用のユーザーを作成
        self.user = User.objects.create_user(
            user_id='testuser',
            password='testpass123',
            store=self.store
        )
        self.url = reverse('common:index')

    def test_index_view_requires_login(self):
        """未認証ユーザーがログインページにリダイレクトされることを確認"""
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 302)
        self.assertIn('/accounts/login/', response.url)

    def test_index_view_authenticated_user(self):
        """認証済みユーザーが200レスポンスを受け取ることを確認"""
        self.client.login(user_id='testuser', password='testpass123')
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)

    def test_index_view_uses_correct_template(self):
        """index()ビューが正しいテンプレートを使用することを確認"""
        self.client.login(user_id='testuser', password='testpass123')
        response = self.client.get(self.url)
        self.assertTemplateUsed(response, 'common/index.html')


class HealthViewTest(TestCase):
    """health()ビューのテスト"""

    def setUp(self):
        """テスト用のクライアントを作成"""
        self.client = Client()
        self.url = reverse('common:health')

    def test_health_view_returns_200(self):
        """ヘルスチェックエンドポイントが200を返すことを確認"""
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)

    def test_health_view_no_authentication_required(self):
        """ヘルスチェックエンドポイントが認証不要であることを確認"""
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertNotEqual(response.status_code, 302)

    def test_health_view_response_type(self):
        """ヘルスチェックエンドポイントのレスポンスタイプを確認"""
        response = self.client.get(self.url)
        self.assertEqual(response['Content-Type'], 'text/html; charset=utf-8')

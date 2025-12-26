from django.test import SimpleTestCase
from django.urls import reverse, resolve
from common import views


class UrlsTest(SimpleTestCase):
    """URLルーティングのテスト"""

    def test_index_url_resolves(self):
        """ルートURLがindex()ビューに解決されることを確認"""
        url = reverse('common:index')
        self.assertEqual(resolve(url).func, views.index)

    def test_health_url_resolves(self):
        """health/URLがhealth()ビューに解決されることを確認"""
        url = reverse('common:health')
        self.assertEqual(resolve(url).func, views.health)

    def test_index_url_name(self):
        """'common:index'が正しいURLを生成することを確認"""
        url = reverse('common:index')
        self.assertEqual(url, '/')

    def test_health_url_name(self):
        """'common:health'が正しいURLを生成することを確認"""
        url = reverse('common:health')
        self.assertEqual(url, '/health/')

from django.test import TestCase
from reports.forms import DailyReportForm

class DailyReportFormTests(TestCase):
    """日報フォームのテスト"""

    def test_valid_form(self):
        """正しい入力データでバリデーションが通るか"""
        data = {
            'genre': 'claim',
            'location': 'kitchen',
            'title': '正常なタイトル',
            'content': '正常な内容',
            'post_to_bbs': False
        }
        form = DailyReportForm(data=data)
        self.assertTrue(form.is_valid())

    def test_invalid_title_empty(self):
        """タイトルが空の場合エラーになるか"""
        data = {
            'genre': 'claim',
            'location': 'kitchen',
            'title': '',  # 空
            'content': '内容はあり',
        }
        form = DailyReportForm(data=data)
        self.assertFalse(form.is_valid())
        self.assertIn('title', form.errors)

    def test_invalid_title_too_long(self):
        """タイトルが200文字を超えた場合エラーになるか"""
        long_title = 'あ' * 201
        data = {
            'genre': 'claim',
            'location': 'kitchen',
            'title': long_title,
            'content': '内容はあり',
        }
        form = DailyReportForm(data=data)
        self.assertFalse(form.is_valid())
        self.assertIn('title', form.errors)

    def test_invalid_content_empty(self):
        """内容が空の場合エラーになるか"""
        data = {
            'genre': 'claim',
            'location': 'kitchen',
            'title': 'タイトル',
            'content': '', # 空
        }
        form = DailyReportForm(data=data)
        self.assertFalse(form.is_valid())
        self.assertIn('content', form.errors)
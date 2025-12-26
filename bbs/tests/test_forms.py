from django.test import TestCase
from bbs.forms import BBSPostForm, BBSCommentForm
# テスト用のダミーデータ作成に必要ならモデルもインポート
# from reports.models import Report (もし日報との紐付けテストを厳密にする場合)

class BBSPostFormTests(TestCase):
    def test_post_form_valid_with_required_fields(self):
        """必須項目（タイトル、ジャンル、本文）が揃っていれば有効であること"""
        # 日報(report)は任意なので含めない
        form_data = {
            'title': 'テストタイトル',
            'genre': 'report',  # 有効な選択肢の一つ
            'content': 'テスト本文です。',
        }
        # __init__で user を pop しているので、引数として渡す（Noneでも動作するか確認）
        form = BBSPostForm(data=form_data, user=None)
        
        self.assertTrue(form.is_valid(), f"バリデーションエラー: {form.errors}")

    def test_post_form_invalid_missing_title(self):
        """タイトルが空の場合は無効であること"""
        form_data = {
            'title': '',
            'genre': 'report',
            'content': 'テスト本文',
        }
        form = BBSPostForm(data=form_data, user=None)
        self.assertFalse(form.is_valid())
        self.assertIn('title', form.errors)

    def test_post_form_invalid_missing_genre(self):
        """ジャンルが選択されていない場合は無効であること"""
        form_data = {
            'title': 'テストタイトル',
            'genre': '', # 空送信
            'content': 'テスト本文',
        }
        form = BBSPostForm(data=form_data, user=None)
        self.assertFalse(form.is_valid())
        self.assertIn('genre', form.errors)

    def test_post_form_invalid_invalid_genre(self):
        """存在しないジャンルが送信された場合は無効であること"""
        form_data = {
            'title': 'テストタイトル',
            'genre': 'unknown_genre', # 定義されていない値
            'content': 'テスト本文',
        }
        form = BBSPostForm(data=form_data, user=None)
        self.assertFalse(form.is_valid())
        self.assertIn('genre', form.errors)

    def test_post_form_report_is_optional(self):
        """レポート（日報）フィールドは任意（空でもOK）であること"""
        form_data = {
            'title': 'テストタイトル',
            'genre': 'claim',
            'content': 'テスト本文',
            'report': '' # 空文字
        }
        form = BBSPostForm(data=form_data, user=None)
        self.assertTrue(form.is_valid())


class BBSCommentFormTests(TestCase):
    def test_comment_form_valid(self):
        """内容があれば有効であること"""
        form_data = {
            'content': 'コメントのテストです',
        }
        form = BBSCommentForm(data=form_data)
        self.assertTrue(form.is_valid())

    def test_comment_form_invalid_empty(self):
        """内容が空の場合は無効であること"""
        form_data = {
            'content': '',
        }
        form = BBSCommentForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn('content', form.errors)
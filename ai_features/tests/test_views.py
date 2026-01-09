from django.test import TestCase, Client, override_settings
from django.urls import reverse
from django.contrib.auth import get_user_model
from unittest.mock import patch, MagicMock
import json

from ai_features.models import AIChatHistory
from stores.models import Store

User = get_user_model()


class ChatPageViewTest(TestCase):
    """chat_page_viewのテスト"""

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

    def test_chat_page_requires_login(self):
        """未認証ユーザーがログインページにリダイレクトされることを確認"""
        response = self.client.get(reverse('ai_features:chat_page'))
        self.assertEqual(response.status_code, 302)
        self.assertIn('/accounts/login/', response.url)

    @override_settings(STREAM_API_URL='http://test.com/stream')
    def test_chat_page_authenticated_user(self):
        """認証済みユーザーがチャットページを表示できることを確認"""
        self.client.login(user_id='testuser', password='testpass123')
        response = self.client.get(reverse('ai_features:chat_page'))

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'ai_features/chat.html')
        self.assertIn('stream_api_url', response.context)


class ChatViewTest(TestCase):
    """ChatViewのテスト"""

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
        self.client.login(user_id='testuser', password='testpass123')
        self.url = reverse('ai_features:chat')

    @patch('ai_features.agents.chat_agent.ChatAgent')
    @patch.dict('os.environ', {'OPENAI_API_KEY': 'test-key', 'OPENAI_MODEL': 'gpt-4o-mini'})
    def test_post_chat_success(self, mock_chat_agent_class):
        """正常なチャットリクエストが成功することを確認"""
        # モックの設定
        mock_agent = MagicMock()
        mock_agent.chat.return_value = {
            'message': 'AIの回答です',
            'sources': [],
            'intermediate_steps': [],
            'token_count': 100
        }
        mock_chat_agent_class.return_value = mock_agent

        # リクエスト送信
        response = self.client.post(
            self.url,
            data=json.dumps({'message': 'こんにちは'}),
            content_type='application/json'
        )

        # 検証
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content)
        self.assertEqual(data['message'], 'AIの回答です')

        # チャット履歴が保存されていることを確認
        self.assertEqual(AIChatHistory.objects.count(), 2)  # user + assistant
        user_chat = AIChatHistory.objects.filter(role='user').first()
        self.assertEqual(user_chat.message, 'こんにちは')

    def test_post_chat_empty_message(self):
        """空のメッセージでエラーが返ることを確認"""
        response = self.client.post(
            self.url,
            data=json.dumps({'message': ''}),
            content_type='application/json'
        )

        self.assertEqual(response.status_code, 400)
        data = json.loads(response.content)
        self.assertIn('error', data)

    def test_post_chat_invalid_json(self):
        """無効なJSONでエラーが返ることを確認"""
        response = self.client.post(
            self.url,
            data='invalid json',
            content_type='application/json'
        )

        self.assertEqual(response.status_code, 400)
        data = json.loads(response.content)
        self.assertIn('error', data)

    @patch.dict('os.environ', {'OPENAI_API_KEY': ''})
    def test_post_chat_missing_api_key(self):
        """API KEYがない場合にエラーが返ることを確認"""
        response = self.client.post(
            self.url,
            data=json.dumps({'message': 'テスト'}),
            content_type='application/json'
        )

        self.assertEqual(response.status_code, 401)
        data = json.loads(response.content)
        self.assertIn('error', data)

    @patch('ai_features.agents.chat_agent.ChatAgent')
    @patch.dict('os.environ', {'OPENAI_API_KEY': 'test-key', 'OPENAI_MODEL': 'gpt-4o-mini'})
    def test_post_chat_with_history(self, mock_chat_agent_class):
        """チャット履歴を含むリクエストが正常に処理されることを確認"""
        # 事前にチャット履歴を作成
        AIChatHistory.objects.create(
            user=self.user,
            role='user',
            message='前の質問'
        )
        AIChatHistory.objects.create(
            user=self.user,
            role='assistant',
            message='前の回答'
        )

        # モックの設定
        mock_agent = MagicMock()
        mock_agent.chat.return_value = {
            'message': '新しい回答',
            'sources': [],
            'intermediate_steps': [],
            'token_count': 150
        }
        mock_chat_agent_class.return_value = mock_agent

        # リクエスト送信
        response = self.client.post(
            self.url,
            data=json.dumps({
                'message': '新しい質問',
                'include_history': True
            }),
            content_type='application/json'
        )

        self.assertEqual(response.status_code, 200)
        # chat_historyがagent.chatに渡されたことを確認
        call_kwargs = mock_agent.chat.call_args[1]
        self.assertIsNotNone(call_kwargs.get('chat_history'))

    def test_get_chat_history(self):
        """GETリクエストでチャット履歴が取得できることを確認"""
        # チャット履歴を作成
        AIChatHistory.objects.create(
            user=self.user,
            role='user',
            message='質問1'
        )
        AIChatHistory.objects.create(
            user=self.user,
            role='assistant',
            message='回答1'
        )

        response = self.client.get(self.url)

        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content)
        self.assertIn('history', data)
        self.assertEqual(len(data['history']), 2)


class ChatHistoryViewTest(TestCase):
    """chat_history_viewのテスト"""

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
        self.client.login(user_id='testuser', password='testpass123')
        self.url = reverse('ai_features:chat_history')

    def test_get_chat_history(self):
        """チャット履歴が正しく取得できることを確認"""
        # チャット履歴を作成
        AIChatHistory.objects.create(
            user=self.user,
            role='user',
            message='質問1'
        )
        AIChatHistory.objects.create(
            user=self.user,
            role='assistant',
            message='回答1'
        )

        response = self.client.get(self.url)

        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content)
        self.assertIn('history', data)
        self.assertEqual(len(data['history']), 2)

    def test_get_chat_history_with_limit(self):
        """limit パラメータが機能することを確認"""
        # 5件のチャット履歴を作成
        for i in range(5):
            AIChatHistory.objects.create(
                user=self.user,
                role='user',
                message=f'質問{i}'
            )

        response = self.client.get(f'{self.url}?limit=3')

        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content)
        self.assertEqual(len(data['history']), 3)

    def test_get_chat_history_ordering(self):
        """履歴が古い順に返されることを確認"""
        chat1 = AIChatHistory.objects.create(
            user=self.user,
            role='user',
            message='最初の質問'
        )
        chat2 = AIChatHistory.objects.create(
            user=self.user,
            role='user',
            message='二番目の質問'
        )

        response = self.client.get(self.url)
        data = json.loads(response.content)

        # 古い順（chat1が先）
        self.assertEqual(data['history'][0]['message'], '最初の質問')
        self.assertEqual(data['history'][1]['message'], '二番目の質問')

    def test_user_isolation(self):
        """他のユーザーの履歴は取得できないことを確認"""
        # 別のユーザーを作成
        other_user = User.objects.create_user(
            user_id='otheruser',
            password='testpass123',
            store=self.store
        )

        # 他のユーザーのチャット履歴を作成
        AIChatHistory.objects.create(
            user=other_user,
            role='user',
            message='他のユーザーの質問'
        )

        # 現在のユーザーのチャット履歴を作成
        AIChatHistory.objects.create(
            user=self.user,
            role='user',
            message='自分の質問'
        )

        response = self.client.get(self.url)
        data = json.loads(response.content)

        # 自分の履歴のみ取得される
        self.assertEqual(len(data['history']), 1)
        self.assertEqual(data['history'][0]['message'], '自分の質問')


class ClearChatHistoryViewTest(TestCase):
    """clear_chat_history_viewのテスト"""

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
        self.client.login(user_id='testuser', password='testpass123')
        self.url = reverse('ai_features:clear_chat_history')

    def test_clear_chat_history(self):
        """チャット履歴が削除されることを確認"""
        # チャット履歴を作成
        AIChatHistory.objects.create(
            user=self.user,
            role='user',
            message='質問1'
        )
        AIChatHistory.objects.create(
            user=self.user,
            role='assistant',
            message='回答1'
        )

        self.assertEqual(AIChatHistory.objects.filter(user=self.user).count(), 2)

        # 削除リクエスト
        response = self.client.delete(self.url)

        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content)
        self.assertIn('message', data)

        # 履歴が削除されていることを確認
        self.assertEqual(AIChatHistory.objects.filter(user=self.user).count(), 0)

    def test_clear_chat_history_user_isolation(self):
        """他のユーザーの履歴は削除されないことを確認"""
        # 別のユーザーを作成
        other_user = User.objects.create_user(
            user_id='otheruser',
            password='testpass123',
            store=self.store
        )

        # 両方のユーザーの履歴を作成
        AIChatHistory.objects.create(
            user=self.user,
            role='user',
            message='自分の質問'
        )
        AIChatHistory.objects.create(
            user=other_user,
            role='user',
            message='他のユーザーの質問'
        )

        # 削除リクエスト
        response = self.client.delete(self.url)

        # 自分の履歴のみ削除
        self.assertEqual(AIChatHistory.objects.filter(user=self.user).count(), 0)
        self.assertEqual(AIChatHistory.objects.filter(user=other_user).count(), 1)


class ChatStreamViewTest(TestCase):
    """chat_stream_viewのテスト"""

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
        self.client.login(user_id='testuser', password='testpass123')
        self.url = reverse('ai_features:chat_stream')

    def test_stream_view_requires_login(self):
        """未認証ユーザーがリダイレクトされることを確認"""
        self.client.logout()
        response = self.client.post(
            self.url,
            data=json.dumps({'message': 'テスト'}),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 302)

    @patch.dict('os.environ', {'OPENAI_API_KEY': ''})
    def test_stream_view_missing_api_key(self):
        """API KEYがない場合にエラーストリームが返ることを確認"""
        response = self.client.post(
            self.url,
            data=json.dumps({'message': 'テスト'}),
            content_type='application/json'
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response['Content-Type'], 'text/event-stream')

        # ストリーミングレスポンスの内容を確認
        content = b''.join(response.streaming_content).decode('utf-8')
        self.assertIn('error', content)
        self.assertIn('API KEY ERROR', content)

    def test_stream_view_empty_message(self):
        """空のメッセージでエラーストリームが返ることを確認"""
        response = self.client.post(
            self.url,
            data=json.dumps({'message': ''}),
            content_type='application/json'
        )

        self.assertEqual(response.status_code, 200)
        content = b''.join(response.streaming_content).decode('utf-8')
        self.assertIn('error', content)

    @patch('ai_features.agents.chat_agent.ChatAgent')
    @patch.dict('os.environ', {'OPENAI_API_KEY': 'test-key', 'OPENAI_MODEL': 'gpt-4o-mini'})
    def test_stream_view_success(self, mock_chat_agent_class):
        """ストリーミングチャットが正常に動作することを確認"""
        # モックの設定
        mock_agent = MagicMock()
        mock_agent.chat_stream.return_value = iter(['こん', 'にち', 'は'])
        mock_chat_agent_class.return_value = mock_agent

        response = self.client.post(
            self.url,
            data=json.dumps({'message': 'テストメッセージ'}),
            content_type='application/json'
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response['Content-Type'], 'text/event-stream')

        # ストリーミングレスポンスの内容を確認
        content = b''.join(response.streaming_content).decode('utf-8')
        self.assertIn('start', content)
        self.assertIn('content', content)
        self.assertIn('done', content)

        # チャット履歴が保存されていることを確認
        self.assertEqual(AIChatHistory.objects.filter(user=self.user).count(), 2)

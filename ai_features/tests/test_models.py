from django.test import TestCase
from django.contrib.auth import get_user_model
from django.utils import timezone
from ai_features.models import AIChatHistory, DocumentVector, KnowledgeVector
from stores.models import Store
import numpy as np

User = get_user_model()


class AIChatHistoryModelTest(TestCase):
    """AIChatHistoryモデルのテスト"""

    def setUp(self):
        """テスト用データを作成"""
        self.store = Store.objects.create(
            store_name='テスト店舗',
            address='テスト住所'
        )
        self.user = User.objects.create_user(
            user_id='testuser',
            password='testpass123',
            store=self.store
        )

    def test_create_chat_history(self):
        """チャット履歴が正常に作成できることを確認"""
        chat = AIChatHistory.objects.create(
            user=self.user,
            role='user',
            message='こんにちは'
        )
        self.assertEqual(chat.user, self.user)
        self.assertEqual(chat.role, 'user')
        self.assertEqual(chat.message, 'こんにちは')
        self.assertIsNotNone(chat.created_at)

    def test_role_choices(self):
        """roleフィールドのchoicesが正しく設定されていることを確認"""
        user_chat = AIChatHistory.objects.create(
            user=self.user,
            role='user',
            message='ユーザーメッセージ'
        )
        assistant_chat = AIChatHistory.objects.create(
            user=self.user,
            role='assistant',
            message='AIメッセージ'
        )
        self.assertEqual(user_chat.get_role_display(), 'ユーザー')
        self.assertEqual(assistant_chat.get_role_display(), 'AI')

    def test_str_method(self):
        """__str__メソッドが正しい形式で文字列を返すことを確認"""
        chat = AIChatHistory.objects.create(
            user=self.user,
            role='user',
            message='テストメッセージ'
        )
        expected_str = f"{self.user} - ユーザー - {chat.created_at}"
        self.assertEqual(str(chat), expected_str)

    def test_ordering(self):
        """チャット履歴がcreated_atの昇順でソートされることを確認"""
        chat1 = AIChatHistory.objects.create(
            user=self.user, role='user', message='最初'
        )
        chat2 = AIChatHistory.objects.create(
            user=self.user, role='assistant', message='二番目'
        )
        chat3 = AIChatHistory.objects.create(
            user=self.user, role='user', message='三番目'
        )

        chats = AIChatHistory.objects.all()
        self.assertEqual(chats[0], chat1)
        self.assertEqual(chats[1], chat2)
        self.assertEqual(chats[2], chat3)

    def test_cascade_delete(self):
        """ユーザー削除時にチャット履歴もカスケード削除されることを確認"""
        AIChatHistory.objects.create(
            user=self.user, role='user', message='テスト'
        )
        self.assertEqual(AIChatHistory.objects.count(), 1)

        self.user.delete()
        self.assertEqual(AIChatHistory.objects.count(), 0)


class DocumentVectorModelTest(TestCase):
    """DocumentVectorモデルのテスト"""

    def setUp(self):
        """テスト用データを作成"""
        self.dummy_embedding = np.random.rand(384).tolist()

    def test_create_document_vector(self):
        """ドキュメントベクトルが正常に作成できることを確認"""
        doc = DocumentVector.objects.create(
            source_type='daily_report',
            source_id=1,
            content='テスト日報の内容',
            metadata={'store_id': 1, 'date': '2024-01-01'},
            embedding=self.dummy_embedding
        )
        self.assertEqual(doc.source_type, 'daily_report')
        self.assertEqual(doc.source_id, 1)
        self.assertEqual(doc.content, 'テスト日報の内容')
        self.assertIsNotNone(doc.created_at)

    def test_source_type_choices(self):
        """source_typeフィールドのchoicesが正しく設定されていることを確認"""
        doc = DocumentVector.objects.create(
            source_type='daily_report',
            source_id=1,
            content='テスト',
            embedding=self.dummy_embedding
        )
        self.assertEqual(doc.get_source_type_display(), '日報')

    def test_unique_together_constraint(self):
        """source_typeとsource_idのユニーク制約が機能することを確認"""
        DocumentVector.objects.create(
            source_type='daily_report',
            source_id=1,
            content='最初のベクトル',
            embedding=self.dummy_embedding
        )

        with self.assertRaises(Exception):
            DocumentVector.objects.create(
                source_type='daily_report',
                source_id=1,
                content='重複するベクトル',
                embedding=self.dummy_embedding
            )

    def test_metadata_default(self):
        """metadataフィールドのデフォルト値が空dictであることを確認"""
        doc = DocumentVector.objects.create(
            source_type='bbs_post',
            source_id=2,
            content='テスト投稿',
            embedding=self.dummy_embedding
        )
        self.assertEqual(doc.metadata, {})

    def test_ordering(self):
        """ドキュメントベクトルがcreated_atの降順でソートされることを確認"""
        doc1 = DocumentVector.objects.create(
            source_type='daily_report', source_id=1,
            content='最初', embedding=self.dummy_embedding
        )
        doc2 = DocumentVector.objects.create(
            source_type='bbs_post', source_id=1,
            content='二番目', embedding=self.dummy_embedding
        )
        doc3 = DocumentVector.objects.create(
            source_type='bbs_comment', source_id=1,
            content='三番目', embedding=self.dummy_embedding
        )

        docs = DocumentVector.objects.all()
        self.assertEqual(docs[0], doc3)
        self.assertEqual(docs[1], doc2)
        self.assertEqual(docs[2], doc1)

    def test_str_method(self):
        """__str__メソッドが正しい形式で文字列を返すことを確認"""
        doc = DocumentVector.objects.create(
            source_type='daily_report',
            source_id=123,
            content='テスト',
            embedding=self.dummy_embedding
        )
        self.assertEqual(str(doc), '日報 - ID:123')


class KnowledgeVectorModelTest(TestCase):
    """KnowledgeVectorモデルのテスト"""

    def setUp(self):
        """テスト用データを作成"""
        self.dummy_embedding = np.random.rand(384).tolist()

    def test_create_knowledge_vector(self):
        """ナレッジベクトルが正常に作成できることを確認"""
        knowledge = KnowledgeVector.objects.create(
            document_type='manual',
            title='テストマニュアル',
            content='マニュアルの内容',
            metadata={'category': 'operations'},
            embedding=self.dummy_embedding
        )
        self.assertEqual(knowledge.document_type, 'manual')
        self.assertEqual(knowledge.title, 'テストマニュアル')
        self.assertEqual(knowledge.content, 'マニュアルの内容')
        self.assertIsNotNone(knowledge.created_at)

    def test_document_type_choices(self):
        """document_typeフィールドのchoicesが正しく設定されていることを確認"""
        knowledge = KnowledgeVector.objects.create(
            document_type='faq',
            title='よくある質問',
            content='FAQの内容',
            embedding=self.dummy_embedding
        )
        self.assertEqual(knowledge.get_document_type_display(), 'FAQ')

    def test_metadata_default(self):
        """metadataフィールドのデフォルト値が空dictであることを確認"""
        knowledge = KnowledgeVector.objects.create(
            document_type='guide',
            title='ガイド',
            content='ガイドの内容',
            embedding=self.dummy_embedding
        )
        self.assertEqual(knowledge.metadata, {})

    def test_ordering(self):
        """ナレッジベクトルがcreated_atの降順でソートされることを確認"""
        k1 = KnowledgeVector.objects.create(
            document_type='manual', title='最初',
            content='内容1', embedding=self.dummy_embedding
        )
        k2 = KnowledgeVector.objects.create(
            document_type='faq', title='二番目',
            content='内容2', embedding=self.dummy_embedding
        )
        k3 = KnowledgeVector.objects.create(
            document_type='policy', title='三番目',
            content='内容3', embedding=self.dummy_embedding
        )

        knowledges = KnowledgeVector.objects.all()
        self.assertEqual(knowledges[0], k3)
        self.assertEqual(knowledges[1], k2)
        self.assertEqual(knowledges[2], k1)

    def test_str_method(self):
        """__str__メソッドが正しい形式で文字列を返すことを確認"""
        knowledge = KnowledgeVector.objects.create(
            document_type='manual',
            title='操作マニュアル',
            content='テスト',
            embedding=self.dummy_embedding
        )
        self.assertEqual(str(knowledge), 'マニュアル - 操作マニュアル')

    def test_updated_at_auto_update(self):
        """updated_atフィールドが自動的に更新されることを確認"""
        knowledge = KnowledgeVector.objects.create(
            document_type='guide',
            title='初期タイトル',
            content='初期内容',
            embedding=self.dummy_embedding
        )
        original_updated_at = knowledge.updated_at

        knowledge.title = '更新されたタイトル'
        knowledge.save()
        knowledge.refresh_from_db()

        self.assertGreater(knowledge.updated_at, original_updated_at)

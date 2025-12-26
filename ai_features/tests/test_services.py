from django.test import TestCase, override_settings
from django.contrib.auth import get_user_model
from unittest.mock import patch, MagicMock
import numpy as np

from ai_features.services.core_services import (
    EmbeddingService,
    QueryClassifier,
    VectorSearchService,
    VectorizationService
)
from ai_features.models import DocumentVector, KnowledgeVector
from stores.models import Store
from reports.models import DailyReport
from bbs.models import BBSPost, BBSComment

User = get_user_model()


class EmbeddingServiceTest(TestCase):
    """EmbeddingServiceのテスト"""

    @patch('ai_features.services.core_services.EmbeddingService.get_local_model')
    @override_settings(DEBUG=True)
    def test_generate_embedding_local_mode(self, mock_get_model):
        """DEBUGモードでローカルembeddingが生成されることを確認"""
        # モックの設定
        mock_model = MagicMock()
        mock_embedding = np.random.rand(384)
        mock_model.encode.return_value = mock_embedding
        mock_get_model.return_value = mock_model

        # テスト実行
        result = EmbeddingService.generate_embedding("テストテキスト")

        # 検証
        self.assertIsNotNone(result)
        self.assertEqual(len(result), 384)
        mock_model.encode.assert_called_once_with("テストテキスト")

    @patch('ai_features.services.core_services.EmbeddingService.get_openai_client')
    @override_settings(DEBUG=False)
    def test_generate_embedding_openai_mode(self, mock_get_client):
        """本番モードでOpenAI embeddingが生成されることを確認"""
        # モックの設定
        mock_client = MagicMock()
        mock_response = MagicMock()
        mock_response.data = [MagicMock()]
        mock_response.data[0].embedding = np.random.rand(384).tolist()
        mock_client.embeddings.create.return_value = mock_response
        mock_get_client.return_value = mock_client

        # テスト実行
        result = EmbeddingService.generate_embedding("テストテキスト")

        # 検証
        self.assertIsNotNone(result)
        self.assertEqual(len(result), 384)
        mock_client.embeddings.create.assert_called_once()

    @patch('ai_features.services.core_services.logger')
    @patch('ai_features.services.core_services.EmbeddingService.get_local_model')
    @override_settings(DEBUG=True)
    def test_generate_embedding_error_handling(self, mock_get_model, mock_logger):
        """エラー時にNoneを返すことを確認"""
        mock_get_model.side_effect = Exception("モデルエラー")

        result = EmbeddingService.generate_embedding("テストテキスト")

        self.assertIsNone(result)
        mock_logger.error.assert_called_once()


class QueryClassifierTest(TestCase):
    """QueryClassifierのテスト"""

    def test_comprehensive_query(self):
        """包括的クエリで正しいTop-K値が返ることを確認"""
        queries = ['全てのクレーム', 'すべての報告', '一覧表示']
        for query in queries:
            with self.subTest(query=query):
                result = QueryClassifier.classify_and_get_top_k(query)
                self.assertEqual(result, 20)

    def test_trend_analysis_query(self):
        """トレンド分析クエリで正しいTop-K値が返ることを確認"""
        queries = ['売上の傾向', '推移を見たい', 'トレンド分析']
        for query in queries:
            with self.subTest(query=query):
                result = QueryClassifier.classify_and_get_top_k(query)
                self.assertEqual(result, 12)

    def test_specific_query(self):
        """特定クエリで正しいTop-K値が返ることを確認"""
        queries = ['昨日のクレーム', '今日の売上', '先週の報告']
        for query in queries:
            with self.subTest(query=query):
                result = QueryClassifier.classify_and_get_top_k(query)
                self.assertEqual(result, 3)

    def test_default_query(self):
        """デフォルトクエリで正しいTop-K値が返ることを確認"""
        queries = ['クレームについて', '何かあった？']
        for query in queries:
            with self.subTest(query=query):
                result = QueryClassifier.classify_and_get_top_k(query)
                self.assertEqual(result, 5)


class VectorSearchServiceTest(TestCase):
    """VectorSearchServiceのテスト"""

    def setUp(self):
        """テスト用データを作成"""
        self.dummy_embedding = np.random.rand(384).tolist()
        self.store = Store.objects.create(
            store_name='テスト店舗',
            address='テスト住所'
        )

        # テスト用のドキュメントベクトルを作成
        DocumentVector.objects.create(
            source_type='daily_report',
            source_id=1,
            content='テスト日報1',
            metadata={'store_id': self.store.store_id, 'date': '2024-01-01'},
            embedding=self.dummy_embedding
        )
        DocumentVector.objects.create(
            source_type='bbs_post',
            source_id=1,
            content='テスト投稿1',
            metadata={'store_id': self.store.store_id, 'date': '2024-01-02'},
            embedding=self.dummy_embedding
        )

        # ナレッジベクトルを作成
        KnowledgeVector.objects.create(
            document_type='manual',
            title='テストマニュアル',
            content='マニュアルの内容',
            metadata={'category': 'operations'},
            embedding=self.dummy_embedding
        )

    @patch('ai_features.services.core_services.EmbeddingService.generate_embedding')
    def test_search_documents_basic(self, mock_generate_embedding):
        """基本的なドキュメント検索が機能することを確認"""
        mock_generate_embedding.return_value = self.dummy_embedding

        results = VectorSearchService.search_documents(
            query='テスト',
            source_types=['daily_report', 'bbs_post'],
            top_k=10
        )

        self.assertEqual(len(results), 2)
        self.assertIn('vector_id', results[0])
        self.assertIn('content', results[0])
        self.assertIn('similarity', results[0])

    @patch('ai_features.services.core_services.EmbeddingService.generate_embedding')
    def test_search_documents_with_store_filter(self, mock_generate_embedding):
        """店舗フィルタが機能することを確認"""
        mock_generate_embedding.return_value = self.dummy_embedding

        results = VectorSearchService.search_documents(
            query='テスト',
            store_id=self.store.store_id,
            source_types=['daily_report'],
            top_k=10
        )

        self.assertGreaterEqual(len(results), 1)
        for result in results:
            self.assertEqual(result['metadata']['store_id'], self.store.store_id)

    @patch('ai_features.services.core_services.EmbeddingService.generate_embedding')
    def test_search_documents_with_date_filter(self, mock_generate_embedding):
        """日付フィルタが機能することを確認"""
        mock_generate_embedding.return_value = self.dummy_embedding

        results = VectorSearchService.search_documents(
            query='テスト',
            source_types=['daily_report', 'bbs_post'],
            filters={'date_from': '2024-01-02'},
            top_k=10
        )

        # date_from以降のみが取得される
        for result in results:
            self.assertGreaterEqual(result['metadata']['date'], '2024-01-02')

    @patch('ai_features.services.core_services.EmbeddingService.generate_embedding')
    def test_search_documents_empty_embedding(self, mock_generate_embedding):
        """embedding生成失敗時に空リストを返すことを確認"""
        mock_generate_embedding.return_value = None

        results = VectorSearchService.search_documents(
            query='テスト',
            source_types=['daily_report'],
            top_k=10
        )

        self.assertEqual(results, [])

    @patch('ai_features.services.core_services.EmbeddingService.generate_embedding')
    def test_search_knowledge_basic(self, mock_generate_embedding):
        """基本的なナレッジ検索が機能することを確認"""
        mock_generate_embedding.return_value = self.dummy_embedding

        results = VectorSearchService.search_knowledge(
            query='マニュアル',
            top_k=5
        )

        self.assertGreaterEqual(len(results), 1)
        self.assertIn('vector_id', results[0])
        self.assertIn('document_type', results[0])
        self.assertIn('similarity', results[0])

    @patch('ai_features.services.core_services.EmbeddingService.generate_embedding')
    def test_search_knowledge_with_category_filter(self, mock_generate_embedding):
        """カテゴリフィルタが機能することを確認"""
        mock_generate_embedding.return_value = self.dummy_embedding

        results = VectorSearchService.search_knowledge(
            query='操作方法',
            category='operations',
            top_k=5
        )

        for result in results:
            self.assertEqual(result['metadata']['category'], 'operations')


class VectorizationServiceTest(TestCase):
    """VectorizationServiceのテスト"""

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

    @patch('ai_features.services.core_services.EmbeddingService.generate_embedding')
    def test_vectorize_daily_report_success(self, mock_generate_embedding):
        """日報のベクトル化が成功することを確認"""
        mock_embedding = np.random.rand(384).tolist()
        mock_generate_embedding.return_value = mock_embedding

        # 日報を作成
        report = DailyReport.objects.create(
            store=self.store,
            user=self.user,
            date='2024-01-01',
            genre='report',
            location='hall',
            title='テスト日報',
            content='日報の内容'
        )

        # ベクトル化実行
        result = VectorizationService.vectorize_daily_report(report.report_id)

        # 検証
        self.assertTrue(result)
        self.assertEqual(DocumentVector.objects.filter(
            source_type='daily_report',
            source_id=report.report_id
        ).count(), 1)

        doc_vector = DocumentVector.objects.get(
            source_type='daily_report',
            source_id=report.report_id
        )
        self.assertEqual(doc_vector.metadata['store_id'], self.store.store_id)
        self.assertEqual(doc_vector.metadata['genre'], 'report')

    @patch('ai_features.services.core_services.EmbeddingService.generate_embedding')
    def test_vectorize_daily_report_update(self, mock_generate_embedding):
        """日報のベクトル化が更新されることを確認（update_or_create）"""
        mock_embedding1 = np.random.rand(384).tolist()
        mock_embedding2 = np.random.rand(384).tolist()

        report = DailyReport.objects.create(
            store=self.store,
            user=self.user,
            date='2024-01-01',
            genre='report',
            location='hall',
            title='最初のタイトル',
            content='最初の内容'
        )

        # 最初のベクトル化
        mock_generate_embedding.return_value = mock_embedding1
        VectorizationService.vectorize_daily_report(report.report_id)

        # 更新
        mock_generate_embedding.return_value = mock_embedding2
        report.title = '更新されたタイトル'
        report.save()
        VectorizationService.vectorize_daily_report(report.report_id)

        # 検証（1つのみ存在し、更新されている）
        self.assertEqual(DocumentVector.objects.filter(
            source_type='daily_report',
            source_id=report.report_id
        ).count(), 1)

    @patch('ai_features.services.core_services.EmbeddingService.generate_embedding')
    def test_vectorize_bbs_post_success(self, mock_generate_embedding):
        """BBS投稿のベクトル化が成功することを確認"""
        mock_embedding = np.random.rand(384).tolist()
        mock_generate_embedding.return_value = mock_embedding

        post = BBSPost.objects.create(
            store=self.store,
            user=self.user,
            title='テスト投稿',
            content='投稿の内容',
            genre='information'
        )

        result = VectorizationService.vectorize_bbs_post(post.post_id)

        self.assertTrue(result)
        self.assertEqual(DocumentVector.objects.filter(
            source_type='bbs_post',
            source_id=post.post_id
        ).count(), 1)

    @patch('ai_features.services.core_services.EmbeddingService.generate_embedding')
    def test_vectorize_bbs_comment_success(self, mock_generate_embedding):
        """BBSコメントのベクトル化が成功することを確認"""
        mock_embedding = np.random.rand(384).tolist()
        mock_generate_embedding.return_value = mock_embedding

        post = BBSPost.objects.create(
            store=self.store,
            user=self.user,
            title='投稿',
            content='内容',
            genre='information'
        )

        comment = BBSComment.objects.create(
            post=post,
            user=self.user,
            content='コメントの内容'
        )

        result = VectorizationService.vectorize_bbs_comment(comment.comment_id)

        self.assertTrue(result)
        self.assertEqual(DocumentVector.objects.filter(
            source_type='bbs_comment',
            source_id=comment.comment_id
        ).count(), 1)

    @patch('ai_features.services.core_services.EmbeddingService.generate_embedding')
    def test_vectorize_embedding_failure(self, mock_generate_embedding):
        """embedding生成失敗時にFalseを返すことを確認"""
        mock_generate_embedding.return_value = None

        report = DailyReport.objects.create(
            store=self.store,
            user=self.user,
            date='2024-01-01',
            genre='report',
            location='hall',
            title='テスト',
            content='内容'
        )

        result = VectorizationService.vectorize_daily_report(report.report_id)

        self.assertFalse(result)
        self.assertEqual(DocumentVector.objects.filter(
            source_type='daily_report',
            source_id=report.report_id
        ).count(), 0)

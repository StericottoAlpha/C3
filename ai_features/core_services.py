"""
AI Features Core Services
ベクトル検索、埋め込み生成、ベクトル化などのコアサービス
"""
import logging
from typing import List, Optional, Dict
import numpy as np

from sentence_transformers import SentenceTransformer

logger = logging.getLogger(__name__)


class EmbeddingService:
    """埋め込みベクトル生成サービス"""

    _model = None

    @classmethod
    def get_model(cls):
        """埋め込みモデルを取得（シングルトン）"""
        if cls._model is None:
            cls._model = SentenceTransformer('paraphrase-multilingual-MiniLM-L12-v2')
        return cls._model

    @classmethod
    def generate_embedding(cls, text: str) -> Optional[List[float]]:
        """テキストから埋め込みベクトルを生成"""
        try:
            model = cls.get_model()
            embedding = model.encode(text)
            return embedding.tolist()
        except Exception as e:
            logger.error(f"Error generating embedding: {e}", exc_info=True)
            return None


class QueryClassifier:
    """クエリを分類してTop-K値を決定"""

    @staticmethod
    def classify_and_get_top_k(query: str) -> int:
        """
        クエリの性質に応じてTop-K値を決定

        - 特定の事例検索（日付指定、店舗指定）→ 3
        - トレンド分析（傾向、推移）→ 12
        - 包括的調査（全て、一覧）→ 20
        - デフォルト → 5
        """
        query_lower = query.lower()

        # 包括的調査
        if any(word in query_lower for word in ['全て', 'すべて', '一覧', 'リスト', '網羅']):
            return 20

        # トレンド分析
        if any(word in query_lower for word in ['傾向', '推移', 'トレンド', '変化', '分析']):
            return 12

        # 特定の事例検索
        if any(word in query_lower for word in ['昨日', '今日', '先週', '先月', '特定']):
            return 3

        # デフォルト
        return 5


class VectorSearchService:
    """ベクトル検索サービス"""

    @staticmethod
    def search_documents(
        query: str,
        user,
        source_types: List[str],
        filters: Optional[Dict] = None,
        top_k: int = 5
    ) -> List[Dict]:
        """
        ドキュメントをベクトル検索

        Args:
            query: 検索クエリ
            user: ユーザーオブジェクト（user.storeでstore情報を取得）
            source_types: 検索対象タイプのリスト ['daily_report', 'bbs_post', 'bbs_comment']
            filters: フィルタ条件（date_from等）
            top_k: 取得件数

        Returns:
            検索結果のリスト
        """
        try:
            from ai_features.models import DocumentVector
            from django.db.models import Q

            # クエリの埋め込みベクトルを生成
            query_embedding = EmbeddingService.generate_embedding(query)
            if query_embedding is None:
                return []

            query_vector = np.array(query_embedding)

            # 基本フィルタ
            queryset = DocumentVector.objects.filter(
                source_type__in=source_types,
                metadata__store_id=user.store.store_id
            )

            # 日付フィルタ
            if filters and 'date_from' in filters:
                queryset = queryset.filter(
                    metadata__date__gte=filters['date_from']
                )

            # ベクトル検索（コサイン類似度で計算）
            results = []
            for doc in queryset:
                doc_vector = np.array(doc.embedding)

                # コサイン類似度を計算
                similarity = np.dot(query_vector, doc_vector) / (
                    np.linalg.norm(query_vector) * np.linalg.norm(doc_vector)
                )

                results.append({
                    'vector_id': doc.vector_id,
                    'source_type': doc.source_type,
                    'source_id': doc.source_id,
                    'content': doc.content,
                    'metadata': doc.metadata,
                    'similarity': float(similarity)
                })

            # 類似度でソートしてTop-Kを返す
            results.sort(key=lambda x: x['similarity'], reverse=True)
            return results[:top_k]

        except Exception as e:
            logger.error(f"Error in vector search: {e}", exc_info=True)
            return []

    @staticmethod
    def search_knowledge(
        query: str,
        category: Optional[str] = None,
        top_k: int = 5
    ) -> List[Dict]:
        """
        ナレッジベースを検索

        Args:
            query: 検索クエリ
            category: カテゴリフィルタ（オプション）
            top_k: 取得件数

        Returns:
            検索結果のリスト
        """
        try:
            from ai_features.models import KnowledgeVector

            # クエリの埋め込みベクトルを生成
            query_embedding = EmbeddingService.generate_embedding(query)
            if query_embedding is None:
                return []

            query_vector = np.array(query_embedding)

            # 基本フィルタ
            queryset = KnowledgeVector.objects.all()

            # カテゴリフィルタ
            if category:
                queryset = queryset.filter(metadata__category=category)

            # ベクトル検索
            results = []
            for knowledge in queryset:
                knowledge_vector = np.array(knowledge.embedding)

                # コサイン類似度を計算
                similarity = np.dot(query_vector, knowledge_vector) / (
                    np.linalg.norm(query_vector) * np.linalg.norm(knowledge_vector)
                )

                results.append({
                    'vector_id': knowledge.vector_id,
                    'document_type': knowledge.document_type,
                    'content': knowledge.content,
                    'metadata': knowledge.metadata,
                    'similarity': float(similarity)
                })

            # 類似度でソートしてTop-Kを返す
            results.sort(key=lambda x: x['similarity'], reverse=True)
            return results[:top_k]

        except Exception as e:
            logger.error(f"Error in knowledge search: {e}", exc_info=True)
            return []


class VectorizationService:
    """ドキュメントのベクトル化サービス"""

    @staticmethod
    def vectorize_daily_report(report_id: int) -> bool:
        """日報をベクトル化"""
        from reports.models import DailyReport
        from ai_features.models import DocumentVector

        try:
            report = DailyReport.objects.get(report_id=report_id)

            # コンテンツ生成
            content_parts = [
                f"日付: {report.date}",
                f"店舗: {report.store.store_name}",
                f"報告者: {report.user.email}",
                f"ジャンル: {report.genre}",
                f"場所: {report.location}",
                f"タイトル: {report.title}",
                f"内容: {report.content}"
            ]

            content = "\n".join(content_parts)

            # ベクトル化
            embedding = EmbeddingService.generate_embedding(content)
            if embedding is None:
                return False

            # メタデータ生成
            metadata = {
                'store_id': report.store.store_id,
                'store_name': report.store.store_name,
                'user_id': report.user.user_id,
                'user_name': report.user.email,
                'date': str(report.date),
                'genre': report.genre,
                'location': report.location,
                'has_claim': report.genre == 'claim',
                'has_praise': report.genre == 'praise',
                'has_accident': report.genre == 'accident',
            }

            # ベクトルを保存/更新
            DocumentVector.objects.update_or_create(
                source_type='daily_report',
                source_id=report_id,
                defaults={
                    'content': content,
                    'metadata': metadata,
                    'embedding': embedding,
                }
            )

            logger.info(f"Vectorized daily report {report_id}")
            return True

        except Exception as e:
            logger.error(f"Error vectorizing daily report {report_id}: {e}", exc_info=True)
            return False

    @staticmethod
    def vectorize_bbs_post(post_id: int) -> bool:
        """掲示板投稿をベクトル化"""
        from bbs.models import BBSPost
        from ai_features.models import DocumentVector

        try:
            post = BBSPost.objects.get(post_id=post_id)

            # コンテンツ生成
            content_parts = [
                f"投稿日: {post.created_at.date()}",
                f"店舗: {post.store.store_name}",
                f"投稿者: {post.user.email}",
                f"タイトル: {post.title}",
                f"内容: {post.content}"
            ]

            content = "\n".join(content_parts)

            # ベクトル化
            embedding = EmbeddingService.generate_embedding(content)
            if embedding is None:
                return False

            # メタデータ生成
            metadata = {
                'store_id': post.store.store_id,
                'store_name': post.store.store_name,
                'author_id': post.user.user_id,
                'author_name': post.user.email,
                'date': str(post.created_at.date()),
                'title': post.title,
            }

            # ベクトルを保存/更新
            DocumentVector.objects.update_or_create(
                source_type='bbs_post',
                source_id=post_id,
                defaults={
                    'content': content,
                    'metadata': metadata,
                    'embedding': embedding,
                }
            )

            logger.info(f"Vectorized BBS post {post_id}")
            return True

        except Exception as e:
            logger.error(f"Error vectorizing BBS post {post_id}: {e}", exc_info=True)
            return False

    @staticmethod
    def vectorize_bbs_comment(comment_id: int) -> bool:
        """掲示板コメントをベクトル化"""
        from bbs.models import BBSComment
        from ai_features.models import DocumentVector

        try:
            comment = BBSComment.objects.get(comment_id=comment_id)

            # コンテンツ生成
            content_parts = [
                f"投稿日: {comment.created_at.date()}",
                f"投稿タイトル: {comment.post.title}",
                f"コメント者: {comment.user.email}",
                f"内容: {comment.content}"
            ]

            content = "\n".join(content_parts)

            # ベクトル化
            embedding = EmbeddingService.generate_embedding(content)
            if embedding is None:
                return False

            # メタデータ生成
            metadata = {
                'post_id': comment.post.post_id,
                'post_title': comment.post.title,
                'author_id': comment.user.user_id,
                'author_name': comment.user.email,
                'date': str(comment.created_at.date()),
            }

            # ベクトルを保存/更新
            DocumentVector.objects.update_or_create(
                source_type='bbs_comment',
                source_id=comment_id,
                defaults={
                    'content': content,
                    'metadata': metadata,
                    'embedding': embedding,
                }
            )

            logger.info(f"Vectorized BBS comment {comment_id}")
            return True

        except Exception as e:
            logger.error(f"Error vectorizing BBS comment {comment_id}: {e}", exc_info=True)
            return False

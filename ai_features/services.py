"""
AI Features Core Services
ٯ��"LLM��ӹn��
"""
import logging
from typing import List, Optional, Dict
import numpy as np

from sentence_transformers import SentenceTransformer

logger = logging.getLogger(__name__)


class EmbeddingService:
    """
    ƭ��ˁ���ӹ
    sentence-transformers�(Wf����gٯ��
    """

    MODEL_NAME = 'paraphrase-multilingual-MiniLM-L12-v2'
    DIMENSION = 384
    _model = None

    @classmethod
    def get_model(cls):
        """���n�����֗"""
        if cls._model is None:
            logger.info(f"Loading embedding model: {cls.MODEL_NAME}")
            cls._model = SentenceTransformer(cls.MODEL_NAME)
        return cls._model

    @classmethod
    def generate_embedding(cls, text: str) -> Optional[List[float]]:
        """
        ƭ��K�ٯ��

        Args:
            text: ٯ��Y�ƭ��

        Returns:
            384!Cnٯ��1WBoNone	
        """
        if not text or not text.strip():
            logger.warning("Empty text provided for embedding")
            return None

        try:
            model = cls.get_model()
            embedding = model.encode(text, convert_to_numpy=True)

            # ��bk	�
            return embedding.tolist()

        except Exception as e:
            logger.error(f"Error generating embedding: {e}")
            return None

    @classmethod
    def generate_embeddings_batch(cls, texts: List[str]) -> List[Optional[List[float]]]:
        """
        pƭ��n���ٯ��

        Args:
            texts: ٯ��Y�ƭ��n��

        Returns:
            ٯ��n��
        """
        if not texts:
            return []

        try:
            model = cls.get_model()

            # z�W�dWf���ï���
            valid_texts = []
            valid_indices = []
            for i, text in enumerate(texts):
                if text and text.strip():
                    valid_texts.append(text)
                    valid_indices.append(i)

            if not valid_texts:
                return [None] * len(texts)

            # ����
            embeddings = model.encode(valid_texts, convert_to_numpy=True, show_progress_bar=True)

            # P��Cn�g��
            results = [None] * len(texts)
            for idx, embedding in zip(valid_indices, embeddings):
                results[idx] = embedding.tolist()

            return results

        except Exception as e:
            logger.error(f"Error in batch embedding generation: {e}")
            return [None] * len(texts)


class VectorizationService:
    """
    ɭ����ٯ����ӹ
    DocumentVector���xnٯ���X
    """

    @classmethod
    def vectorize_daily_report(cls, report_id: int) -> bool:
        """
        �1�ٯ��

        Args:
            report_id: �1ID

        Returns:
            �W_�True
        """
        from reports.models import DailyReport
        from ai_features.models import DocumentVector

        try:
            report = DailyReport.objects.get(report_id=report_id)

            # �������
            content_parts = [
                f"�1: {report.report_date}",
                f"�: {report.store.store_name}",
                f"\: {report.user.get_full_name() or report.user.username}",
            ]

            # ����n�����
            if report.claim_content:
                content_parts.append(f"����: {report.claim_content}")
            if report.praise_content:
                content_parts.append(f"��: {report.praise_content}")
            if report.accident_content:
                content_parts.append(f"�E: {report.accident_content}")
            if report.other_content:
                content_parts.append(f"]n�: {report.other_content}")

            content = "\n".join(content_parts)

            # ٯ��
            embedding = EmbeddingService.generate_embedding(content)
            if embedding is None:
                return False

            # ������
            metadata = {
                'store_id': report.store.store_id,
                'store_name': report.store.store_name,
                'user_id': report.user.user_id,
                'user_name': report.user.get_full_name() or report.user.username,
                'date': str(report.report_date),
                'has_claim': bool(report.claim_content),
                'has_praise': bool(report.praise_content),
                'has_accident': bool(report.accident_content),
            }

            # �Xnٯ����~_o\
            DocumentVector.objects.update_or_create(
                source_type='daily_report',
                source_id=report_id,
                defaults={
                    'content': content,
                    'metadata': metadata,
                    'embedding': embedding,
                }
            )

            return True

        except Exception as e:
            logger.error(f"Error vectorizing daily report {report_id}: {e}")
            return False

    @classmethod
    def vectorize_bbs_post(cls, post_id: int) -> bool:
        """
        �:�?�ٯ��

        Args:
            post_id: �?ID

        Returns:
            �W_�True
        """
        from bbs.models import BBSPost
        from ai_features.models import DocumentVector

        try:
            post = BBSPost.objects.get(post_id=post_id)

            # �������
            content = f"����: {post.title}\n��: {post.content}"

            # ٯ��
            embedding = EmbeddingService.generate_embedding(content)
            if embedding is None:
                return False

            # ������
            metadata = {
                'store_id': post.store.store_id,
                'store_name': post.store.store_name,
                'author_id': post.author.user_id,
                'author_name': post.author.get_full_name() or post.author.username,
                'title': post.title,
                'category': post.category,
                'date': str(post.created_at.date()),
            }

            # �Xnٯ����~_o\
            DocumentVector.objects.update_or_create(
                source_type='bbs_post',
                source_id=post_id,
                defaults={
                    'content': content,
                    'metadata': metadata,
                    'embedding': embedding,
                }
            )

            return True

        except Exception as e:
            logger.error(f"Error vectorizing BBS post {post_id}: {e}")
            return False

    @classmethod
    def vectorize_bbs_comment(cls, comment_id: int) -> bool:
        """
        �:���Ȓٯ��

        Args:
            comment_id: ����ID

        Returns:
            �W_�True
        """
        from bbs.models import BBSComment
        from ai_features.models import DocumentVector

        try:
            comment = BBSComment.objects.get(comment_id=comment_id)

            # ���������?�1�+��	
            content = f"�?����: {comment.post.title}\n����: {comment.content}"

            # ٯ��
            embedding = EmbeddingService.generate_embedding(content)
            if embedding is None:
                return False

            # ������
            metadata = {
                'store_id': comment.post.store.store_id,
                'store_name': comment.post.store.store_name,
                'author_id': comment.author.user_id,
                'author_name': comment.author.get_full_name() or comment.author.username,
                'post_id': comment.post.post_id,
                'post_title': comment.post.title,
                'date': str(comment.created_at.date()),
            }

            # �Xnٯ����~_o\
            DocumentVector.objects.update_or_create(
                source_type='bbs_comment',
                source_id=comment_id,
                defaults={
                    'content': content,
                    'metadata': metadata,
                    'embedding': embedding,
                }
            )

            return True

        except Exception as e:
            logger.error(f"Error vectorizing BBS comment {comment_id}: {e}")
            return False


class VectorSearchService:
    """
    ベクトル検索サービス
    PgVectorを使用したコサイン類似度検索
    """

    @classmethod
    def search_documents(
        cls,
        query: str,
        user,
        source_types: Optional[List[str]] = None,
        filters: Optional[Dict] = None,
        top_k: int = 5
    ) -> List[Dict]:
        """
        実績RAG検索（DocumentVector）

        Args:
            query: 検索クエリ
            user: ユーザーオブジェクト
            source_types: ソースタイプのリスト（['daily_report', 'bbs_post']等）
            filters: メタデータフィルタ（store_id, date等）
            top_k: 取得件数

        Returns:
            検索結果のリスト
        """
        from ai_features.models import DocumentVector
        from django.db import connection

        # クエリベクトル生成
        query_embedding = EmbeddingService.generate_embedding(query)
        if query_embedding is None:
            logger.error("Failed to generate query embedding")
            return []

        # WHERE句構築
        where_clauses = []
        params = [query_embedding]

        # ユーザーの店舗でフィルタ
        if hasattr(user, 'store'):
            where_clauses.append("metadata->>'store_id' = %s")
            params.append(str(user.store.store_id))

        # ソースタイプフィルタ
        if source_types:
            placeholders = ','.join(['%s'] * len(source_types))
            where_clauses.append(f"source_type IN ({placeholders})")
            params.extend(source_types)

        # 追加フィルタ
        if filters:
            for key, value in filters.items():
                if key == 'date':
                    where_clauses.append("metadata->>'date' = %s")
                    params.append(str(value))
                elif key == 'date_from':
                    where_clauses.append("metadata->>'date' >= %s")
                    params.append(str(value))
                elif key == 'date_to':
                    where_clauses.append("metadata->>'date' <= %s")
                    params.append(str(value))
                elif key == 'genre':
                    where_clauses.append("metadata->>'genre' = %s")
                    params.append(str(value))
                elif key == 'user_id':
                    where_clauses.append("metadata->>'user_id' = %s")
                    params.append(str(value))

        where_clause = " AND ".join(where_clauses) if where_clauses else "1=1"

        # パラメータにquery_embeddingとtop_kを追加
        params.append(query_embedding)
        params.append(top_k)

        # SQL実行
        sql = f"""
            SELECT
                vector_id,
                source_type,
                source_id,
                content,
                metadata,
                1 - (embedding <=> %s::vector) AS similarity
            FROM document_vectors
            WHERE {where_clause}
            ORDER BY embedding <=> %s::vector
            LIMIT %s
        """

        try:
            with connection.cursor() as cursor:
                cursor.execute(sql, params)
                columns = [col[0] for col in cursor.description]
                results = [dict(zip(columns, row)) for row in cursor.fetchall()]

            return results

        except Exception as e:
            logger.error(f"Error in vector search: {e}")
            return []

    @classmethod
    def search_knowledge(
        cls,
        query: str,
        category: Optional[str] = None,
        document_type: Optional[str] = None,
        top_k: int = 3
    ) -> List[Dict]:
        """
        ナレッジRAG検索（KnowledgeVector）

        Args:
            query: 検索クエリ
            category: カテゴリフィルタ（'hygiene', 'service'等）
            document_type: ドキュメントタイプフィルタ（'manual', 'guideline'等）
            top_k: 取得件数

        Returns:
            検索結果のリスト
        """
        from ai_features.models import KnowledgeVector
        from django.db import connection

        # クエリベクトル生成
        query_embedding = EmbeddingService.generate_embedding(query)
        if query_embedding is None:
            logger.error("Failed to generate query embedding")
            return []

        # WHERE句構築
        where_clauses = []
        params = [query_embedding]

        if category:
            where_clauses.append("metadata->>'category' = %s")
            params.append(category)

        if document_type:
            where_clauses.append("document_type = %s")
            params.append(document_type)

        where_clause = " AND ".join(where_clauses) if where_clauses else "1=1"

        # パラメータにquery_embeddingとtop_kを追加
        params.append(query_embedding)
        params.append(top_k)

        # SQL実行
        sql = f"""
            SELECT
                vector_id,
                document_id,
                document_type,
                content,
                metadata,
                1 - (embedding <=> %s::vector) AS similarity
            FROM knowledge_vectors
            WHERE {where_clause}
            ORDER BY embedding <=> %s::vector
            LIMIT %s
        """

        try:
            with connection.cursor() as cursor:
                cursor.execute(sql, params)
                columns = [col[0] for col in cursor.description]
                results = [dict(zip(columns, row)) for row in cursor.fetchall()]

            return results

        except Exception as e:
            logger.error(f"Error in knowledge vector search: {e}")
            return []


class QueryClassifier:
    """
    クエリ分類サービス
    クエリの性質に応じて動的にTop-K値を決定
    """

    @classmethod
    def classify_and_get_top_k(cls, query: str) -> int:
        """
        クエリの性質に応じてTop-K値を決定

        Args:
            query: 検索クエリ

        Returns:
            推奨Top-K値
        """
        # 特定の事例検索（明確）→ 少なめ
        if any(keyword in query for keyword in ['店', '日', '月', 'ID']):
            # 日付や店舗が指定されている = 明確なクエリ
            return 3

        # トレンド分析（傾向把握）→ 中程度
        if any(keyword in query for keyword in ['傾向', '多い', '増加', '減少', '推移']):
            return 12

        # 包括的調査（全体像）→ 多め
        if any(keyword in query for keyword in ['全て', '一覧', 'すべて', '全体']):
            return 20

        # デフォルト
        return 5

    @classmethod
    def is_ambiguous(cls, query: str) -> bool:
        """
        クエリが曖昧かどうかを判定

        Args:
            query: 検索クエリ

        Returns:
            曖昧ならTrue
        """
        # 曖昧な時間表現
        ambiguous_time = ['昨日', '前日', '最近', '先週', '先月', '今週', '今月']
        if any(word in query for word in ambiguous_time):
            return True

        # 抽象的な表現
        ambiguous_terms = ['問題', 'トラブル', '件', 'こと', 'もの', 'やつ']
        if any(word in query for word in ambiguous_terms):
            # 具体的な日付や名前がない場合のみ曖昧と判定
            if not any(char.isdigit() for char in query):
                return True

        return False

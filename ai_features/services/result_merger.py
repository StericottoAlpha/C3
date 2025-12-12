"""
結果統合・ランキングサービス
複数クエリからの検索結果を統合してスコアリング
"""
import logging
from typing import List, Dict
from collections import defaultdict

logger = logging.getLogger(__name__)


class ResultMerger:
    """
    検索結果統合サービス

    機能:
    - 重複排除（source_type, source_idでグルーピング）
    - スコアリング: ヒット回数 × 10 + 最大類似度
    - 最終スコア降順ソート
    - Top-K件を返却
    """

    @classmethod
    def merge_and_rank(
        cls,
        search_results_list: List[List[Dict]],
        top_k: int = 10
    ) -> List[Dict]:
        """
        複数の検索結果を統合してランキング

        Args:
            search_results_list: 検索結果のリスト
                [
                    [{'vector_id': 1, 'source_type': 'daily_report', 'source_id': 123, 'similarity': 0.85, ...}, ...],
                    [{'vector_id': 2, 'source_type': 'daily_report', 'source_id': 123, 'similarity': 0.82, ...}, ...],
                    ...
                ]
            top_k: 返却する上位件数

        Returns:
            統合・ランキングされた結果
            [
                {
                    'source_type': 'daily_report',
                    'source_id': 123,
                    'content': '...',
                    'metadata': {...},
                    'hit_count': 3,
                    'max_similarity': 0.85,
                    'avg_similarity': 0.80,
                    'final_score': 30.85,
                },
                ...
            ]
        """
        if not search_results_list:
            return []

        # (source_type, source_id)でグルーピング
        grouped = defaultdict(list)

        for results in search_results_list:
            for item in results:
                key = (item['source_type'], item['source_id'])
                grouped[key].append(item)

        # スコアリング
        ranked_results = []
        for (source_type, source_id), items in grouped.items():
            # ヒット回数
            hit_count = len(items)

            # 類似度統計
            similarities = [item['similarity'] for item in items]
            max_similarity = max(similarities)
            avg_similarity = sum(similarities) / len(similarities)

            # 最終スコア: ヒット回数 × 10 + 最大類似度
            final_score = hit_count * 10 + max_similarity

            # 最も類似度が高いアイテムを代表として使用
            best_item = max(items, key=lambda x: x['similarity'])

            ranked_results.append({
                'source_type': source_type,
                'source_id': source_id,
                'content': best_item['content'],
                'metadata': best_item['metadata'],
                'hit_count': hit_count,
                'max_similarity': round(max_similarity, 4),
                'avg_similarity': round(avg_similarity, 4),
                'final_score': round(final_score, 4),
            })

        # 最終スコア降順ソート
        ranked_results.sort(key=lambda x: x['final_score'], reverse=True)

        # Top-K件を返却
        return ranked_results[:top_k]

    @classmethod
    def merge_simple(
        cls,
        search_results_list: List[List[Dict]],
        top_k: int = 10
    ) -> List[Dict]:
        """
        シンプルな統合（重複排除のみ、スコアリングなし）

        Args:
            search_results_list: 検索結果のリスト
            top_k: 返却する上位件数

        Returns:
            重複排除された結果（類似度順）
        """
        if not search_results_list:
            return []

        # すべての結果を統合
        all_results = []
        for results in search_results_list:
            all_results.extend(results)

        # (source_type, source_id)で重複排除
        seen = set()
        unique_results = []

        for item in all_results:
            key = (item['source_type'], item['source_id'])
            if key not in seen:
                seen.add(key)
                unique_results.append(item)

        # 類似度降順ソート
        unique_results.sort(key=lambda x: x['similarity'], reverse=True)

        # Top-K件を返却
        return unique_results[:top_k]

    @classmethod
    def deduplicate(
        cls,
        results: List[Dict]
    ) -> List[Dict]:
        """
        単一結果セット内の重複排除

        Args:
            results: 検索結果

        Returns:
            重複排除された結果
        """
        seen = set()
        unique = []

        for item in results:
            key = (item['source_type'], item['source_id'])
            if key not in seen:
                seen.add(key)
                unique.append(item)

        return unique

    @classmethod
    def filter_by_threshold(
        cls,
        results: List[Dict],
        min_similarity: float = 0.3
    ) -> List[Dict]:
        """
        類似度閾値でフィルタリング

        Args:
            results: 検索結果
            min_similarity: 最小類似度（0.0-1.0）

        Returns:
            フィルタリングされた結果
        """
        return [
            item for item in results
            if item.get('similarity', 0) >= min_similarity
        ]

    @classmethod
    def group_by_source_type(
        cls,
        results: List[Dict]
    ) -> Dict[str, List[Dict]]:
        """
        source_typeでグルーピング

        Args:
            results: 検索結果

        Returns:
            source_typeごとの結果
            {
                'daily_report': [...],
                'bbs_post': [...],
                'bbs_comment': [...],
            }
        """
        grouped = defaultdict(list)

        for item in results:
            source_type = item['source_type']
            grouped[source_type].append(item)

        return dict(grouped)

    @classmethod
    def rerank_with_weights(
        cls,
        results: List[Dict],
        weights: Dict[str, float]
    ) -> List[Dict]:
        """
        source_typeごとの重みで再ランキング

        Args:
            results: 検索結果
            weights: source_typeごとの重み
                {
                    'daily_report': 1.0,
                    'bbs_post': 0.8,
                    'bbs_comment': 0.6,
                }

        Returns:
            再ランキングされた結果
        """
        for item in results:
            source_type = item['source_type']
            weight = weights.get(source_type, 1.0)
            original_similarity = item.get('similarity', 0)

            # 重み付き類似度
            item['weighted_similarity'] = original_similarity * weight
            item['weight'] = weight

        # 重み付き類似度降順ソート
        results.sort(key=lambda x: x['weighted_similarity'], reverse=True)

        return results

    @classmethod
    def enhance_with_metadata(
        cls,
        results: List[Dict]
    ) -> List[Dict]:
        """
        メタデータを追加して結果を強化

        Args:
            results: 検索結果

        Returns:
            強化された結果
        """
        for item in results:
            metadata = item.get('metadata', {})

            # 表示用の追加情報
            item['display_info'] = {
                'source_label': cls._get_source_label(item['source_type']),
                'date': metadata.get('date', '不明'),
                'store_name': metadata.get('store_name', '不明'),
                'author_name': metadata.get('user_name') or metadata.get('author_name', '不明'),
            }

            # コンテンツプレビュー（最初の100文字）
            content = item.get('content', '')
            item['preview'] = content[:100] + ('...' if len(content) > 100 else '')

        return results

    @classmethod
    def _get_source_label(cls, source_type: str) -> str:
        """
        source_typeの日本語ラベル取得

        Args:
            source_type: ソースタイプ

        Returns:
            日本語ラベル
        """
        labels = {
            'daily_report': '日報',
            'bbs_post': '掲示板投稿',
            'bbs_comment': '掲示板コメント',
        }
        return labels.get(source_type, source_type)

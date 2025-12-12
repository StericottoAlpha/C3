"""
検索ツール
LangChain Function Calling Agent用の検索ツール
"""
import logging
from typing import List, Dict, Optional
from langchain.tools import tool

from ai_features.services import VectorSearchService, QueryExpander, ResultMerger, QueryClassifier

logger = logging.getLogger(__name__)


@tool
def search_past_cases(
    query: str,
    user,
    source_types: Optional[List[str]] = None,
    date_from: Optional[str] = None,
    date_to: Optional[str] = None,
    top_k: Optional[int] = None
) -> str:
    """
    過去の実績データを検索（日報、掲示板投稿・コメント）

    このツールは明確なクエリ（具体的な日付や店舗が指定されている）に使用してください。
    曖昧なクエリの場合は expand_and_search_cases を使用してください。

    Args:
        query: 検索クエリ（例: "2025-12-09のクレーム内容", "先週の売上報告"）
        user: ユーザーオブジェクト
        source_types: 検索対象タイプ（例: ["daily_report", "bbs_post"]）。Noneの場合は全て検索
        date_from: 開始日（YYYY-MM-DD形式、オプション）
        date_to: 終了日（YYYY-MM-DD形式、オプション）
        top_k: 取得件数（オプション、自動判定される）

    Returns:
        検索結果のJSON文字列
    """
    try:
        # Top-K自動判定
        if top_k is None:
            top_k = QueryClassifier.classify_and_get_top_k(query)

        # フィルタ構築
        filters = {}
        if date_from:
            filters['date_from'] = date_from
        if date_to:
            filters['date_to'] = date_to

        # 検索実行
        results = VectorSearchService.search_documents(
            query=query,
            user=user,
            source_types=source_types,
            filters=filters,
            top_k=top_k
        )

        # 結果強化
        results = ResultMerger.enhance_with_metadata(results)

        # 結果フォーマット
        if not results:
            return "該当する実績データが見つかりませんでした。"

        # 結果を整形
        formatted_results = []
        for idx, item in enumerate(results, 1):
            display_info = item.get('display_info', {})
            formatted_results.append({
                'rank': idx,
                'source': display_info.get('source_label', item['source_type']),
                'date': display_info.get('date', '不明'),
                'store': display_info.get('store_name', '不明'),
                'author': display_info.get('author_name', '不明'),
                'similarity': f"{item['similarity']:.2%}",
                'content': item.get('preview', item['content'][:200]),
                'metadata': item.get('metadata', {}),
            })

        import json
        return json.dumps(formatted_results, ensure_ascii=False, indent=2)

    except Exception as e:
        logger.error(f"Error in search_past_cases: {e}")
        return f"検索中にエラーが発生しました: {str(e)}"


@tool
def expand_and_search_cases(
    query: str,
    user,
    source_types: Optional[List[str]] = None,
    top_k: Optional[int] = None
) -> str:
    """
    曖昧なクエリを展開して過去の実績データを検索

    このツールは曖昧なクエリ（「昨日の問題」「最近のトラブル」など）に使用してください。
    LLMでクエリを3-5個の具体的なクエリに展開し、複数検索を実行して結果を統合します。

    Args:
        query: 曖昧な検索クエリ（例: "昨日の問題", "最近のクレーム"）
        user: ユーザーオブジェクト
        source_types: 検索対象タイプ（例: ["daily_report"]）。Noneの場合は全て検索
        top_k: 最終的な取得件数（オプション、自動判定される）

    Returns:
        統合された検索結果のJSON文字列
    """
    try:
        # Top-K自動判定
        if top_k is None:
            top_k = QueryClassifier.classify_and_get_top_k(query)

        # クエリ展開
        expanded_queries = QueryExpander.expand(query, user)
        logger.info(f"Expanded queries: {expanded_queries}")

        # 各クエリで検索
        all_results = []
        for expanded_query in expanded_queries:
            results = VectorSearchService.search_documents(
                query=expanded_query,
                user=user,
                source_types=source_types,
                filters=None,
                top_k=top_k  # 各クエリから同じ件数取得
            )
            all_results.append(results)

        # 結果統合・ランキング
        merged_results = ResultMerger.merge_and_rank(all_results, top_k=top_k)

        # 結果強化
        merged_results = ResultMerger.enhance_with_metadata(merged_results)

        # 結果フォーマット
        if not merged_results:
            return "該当する実績データが見つかりませんでした。"

        # 結果を整形
        formatted_results = []
        for idx, item in enumerate(merged_results, 1):
            display_info = item.get('display_info', {})
            formatted_results.append({
                'rank': idx,
                'source': display_info.get('source_label', item['source_type']),
                'date': display_info.get('date', '不明'),
                'store': display_info.get('store_name', '不明'),
                'author': display_info.get('author_name', '不明'),
                'hit_count': item.get('hit_count', 1),
                'max_similarity': f"{item.get('max_similarity', 0):.2%}",
                'final_score': f"{item.get('final_score', 0):.2f}",
                'content': item.get('preview', item['content'][:200]),
                'metadata': item.get('metadata', {}),
            })

        import json
        result_json = json.dumps({
            'original_query': query,
            'expanded_queries': expanded_queries,
            'results': formatted_results
        }, ensure_ascii=False, indent=2)

        return result_json

    except Exception as e:
        logger.error(f"Error in expand_and_search_cases: {e}")
        return f"検索中にエラーが発生しました: {str(e)}"


@tool
def search_manual(
    query: str,
    category: Optional[str] = None,
    document_type: Optional[str] = None,
    top_k: int = 3
) -> str:
    """
    マニュアル・ガイドライン・手順書を検索

    衛生管理、接客サービス、オペレーション、クレーム対応などの
    公式マニュアルから情報を検索します。

    Args:
        query: 検索クエリ（例: "食中毒の予防方法", "クレーム対応の手順"）
        category: カテゴリフィルタ（hygiene, service, operation, complaint等、オプション）
        document_type: ドキュメントタイプフィルタ（manual, guideline, procedure等、オプション）
        top_k: 取得件数（デフォルト: 3）

    Returns:
        検索結果のJSON文字列
    """
    try:
        # 検索実行
        results = VectorSearchService.search_knowledge(
            query=query,
            category=category,
            document_type=document_type,
            top_k=top_k
        )

        # 結果フォーマット
        if not results:
            return "該当するマニュアルが見つかりませんでした。"

        # 結果を整形
        formatted_results = []
        for idx, item in enumerate(results, 1):
            metadata = item.get('metadata', {})
            formatted_results.append({
                'rank': idx,
                'document': metadata.get('document_title', '不明'),
                'category': metadata.get('category', '不明'),
                'document_type': item.get('document_type', '不明'),
                'version': metadata.get('version', '不明'),
                'similarity': f"{item['similarity']:.2%}",
                'content': item['content'][:300] + ('...' if len(item['content']) > 300 else ''),
                'chapter': metadata.get('section_header', ''),
                'chunk_index': metadata.get('chunk_index', 0),
            })

        import json
        return json.dumps(formatted_results, ensure_ascii=False, indent=2)

    except Exception as e:
        logger.error(f"Error in search_manual: {e}")
        return f"検索中にエラーが発生しました: {str(e)}"

"""
検索ツール（store_id引数版）
LangChain @tool デコレータを使用
"""
import logging
import json
from typing import Optional

from langchain_core.tools import tool

logger = logging.getLogger(__name__)


@tool
def search_daily_reports(query: str, store_id: int, days: int = 30) -> str:
    """
    日報データを検索します。過去の報告、クレーム、賞賛、事故などを検索できます。

    Args:
        query: 検索クエリ（例: "先週のクレーム", "昨日の売上報告"）
        store_id: 店舗ID
        days: 検索対象日数（デフォルト: 30日）

    Returns:
        検索結果のJSON文字列
    """
    try:
        from ai_features.core_services import VectorSearchService, QueryClassifier
        from datetime import date, timedelta
        from stores.models import Store

        # 擬似userオブジェクトを作成（store情報のみ）
        class PseudoUser:
            def __init__(self, store):
                self.store = store

        store = Store.objects.get(store_id=store_id)
        pseudo_user = PseudoUser(store)

        # クエリの性質に応じてTop-K値を決定
        top_k = QueryClassifier.classify_and_get_top_k(query)

        # 日付フィルタ
        date_from = (date.today() - timedelta(days=days)).isoformat()

        # ベクトル検索実行
        search_results = VectorSearchService.search_documents(
            query=query,
            user=pseudo_user,
            source_types=['daily_report'],
            filters={'date_from': date_from},
            top_k=top_k
        )

        # 結果を整形
        formatted_results = []
        for item in search_results:
            metadata = item.get('metadata', {})
            formatted_results.append({
                "date": metadata.get('date', '不明'),
                "type": "日報",
                "store_name": metadata.get('store_name', '不明'),
                "user_name": metadata.get('user_name', '不明'),
                "content": item.get('content', ''),
                "similarity": round(float(item.get('similarity', 0)), 3),
                "has_claim": metadata.get('has_claim', False),
                "has_praise": metadata.get('has_praise', False),
                "has_accident": metadata.get('has_accident', False),
            })

        result = {
            "status": "success",
            "query": query,
            "store_id": store_id,
            "days": days,
            "top_k": top_k,
            "results": formatted_results,
            "total": len(formatted_results)
        }

        return json.dumps(result, ensure_ascii=False, indent=2)

    except Exception as e:
        logger.error(f"Error in search_daily_reports: {e}", exc_info=True)
        return json.dumps({
            "status": "error",
            "message": f"検索エラー: {str(e)}"
        }, ensure_ascii=False)


@tool
def search_bbs_posts(query: str, store_id: int, days: int = 30) -> str:
    """
    掲示板の投稿とコメントを検索します。店舗内のコミュニケーション履歴を確認できます。

    Args:
        query: 検索クエリ（例: "シフト調整", "設備トラブル"）
        store_id: 店舗ID
        days: 検索対象日数（デフォルト: 30日）

    Returns:
        検索結果のJSON文字列
    """
    try:
        from ai_features.core_services import VectorSearchService, QueryClassifier
        from datetime import date, timedelta
        from stores.models import Store

        # 擬似userオブジェクトを作成
        class PseudoUser:
            def __init__(self, store):
                self.store = store

        store = Store.objects.get(store_id=store_id)
        pseudo_user = PseudoUser(store)

        # クエリの性質に応じてTop-K値を決定
        top_k = QueryClassifier.classify_and_get_top_k(query)

        # 日付フィルタ
        date_from = (date.today() - timedelta(days=days)).isoformat()

        # ベクトル検索実行（投稿とコメント両方）
        search_results = VectorSearchService.search_documents(
            query=query,
            user=pseudo_user,
            source_types=['bbs_post', 'bbs_comment'],
            filters={'date_from': date_from},
            top_k=top_k
        )

        # 結果を整形
        formatted_results = []
        for item in search_results:
            metadata = item.get('metadata', {})
            source_type = item.get('source_type', '')

            if source_type == 'bbs_post':
                formatted_results.append({
                    "date": metadata.get('date', '不明'),
                    "type": "投稿",
                    "title": metadata.get('title', '不明'),
                    "author": metadata.get('author_name', '不明'),
                    "category": metadata.get('category', '未分類'),
                    "content": item.get('content', ''),
                    "similarity": round(float(item.get('similarity', 0)), 3)
                })
            elif source_type == 'bbs_comment':
                formatted_results.append({
                    "date": metadata.get('date', '不明'),
                    "type": "コメント",
                    "post_title": metadata.get('post_title', '不明'),
                    "author": metadata.get('author_name', '不明'),
                    "content": item.get('content', ''),
                    "similarity": round(float(item.get('similarity', 0)), 3)
                })

        result = {
            "status": "success",
            "query": query,
            "store_id": store_id,
            "days": days,
            "top_k": top_k,
            "results": formatted_results,
            "total": len(formatted_results)
        }

        return json.dumps(result, ensure_ascii=False, indent=2)

    except Exception as e:
        logger.error(f"Error in search_bbs_posts: {e}", exc_info=True)
        return json.dumps({
            "status": "error",
            "message": f"検索エラー: {str(e)}"
        }, ensure_ascii=False)


@tool
def search_manual(query: str, category: Optional[str] = None) -> str:
    """
    業務マニュアル・ガイドライン・手順書を検索します。全店舗共通のナレッジベースです。

    Args:
        query: 検索クエリ（例: "クレーム対応手順", "食中毒予防"）
        category: カテゴリフィルタ（例: "衛生管理", "接客", "調理"）省略可能

    Returns:
        検索結果のJSON文字列
    """
    try:
        from ai_features.core_services import VectorSearchService

        # ナレッジベクトル検索実行
        search_results = VectorSearchService.search_knowledge(
            query=query,
            category=category,
            top_k=5
        )

        # 結果を整形
        formatted_results = []
        for item in search_results:
            metadata = item.get('metadata', {})
            formatted_results.append({
                "document_type": item.get('document_type', '不明'),
                "category": metadata.get('category', '未分類'),
                "title": metadata.get('title', '不明'),
                "section": metadata.get('section', ''),
                "content": item.get('content', ''),
                "similarity": round(float(item.get('similarity', 0)), 3)
            })

        result = {
            "status": "success",
            "query": query,
            "category": category,
            "results": formatted_results,
            "total": len(formatted_results)
        }

        return json.dumps(result, ensure_ascii=False, indent=2)

    except Exception as e:
        logger.error(f"Error in search_manual: {e}", exc_info=True)
        return json.dumps({
            "status": "error",
            "message": f"検索エラー: {str(e)}"
        }, ensure_ascii=False)

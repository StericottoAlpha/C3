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
def search_daily_reports(query: str = "", store_id: int = 0, days: int = 60) -> str:
    """
    自店舗の日報データを検索します。過去の報告、クレーム、賞賛、事故などを検索できます。

    Args:
        query: 検索クエリ（例: "先週のクレーム", "昨日の売上報告"）
        store_id: 店舗ID
        days: 検索対象日数（デフォルト: 60日）

    Returns:
        検索結果のJSON文字列
    """
    try:
        from ai_features.services.core_services import VectorSearchService, QueryClassifier
        from datetime import date, timedelta

        # クエリの性質に応じてTop-K値を決定
        top_k = QueryClassifier.classify_and_get_top_k(query)

        # 日付フィルタ
        date_from = (date.today() - timedelta(days=days)).isoformat()

        # ベクトル検索実行
        search_results = VectorSearchService.search_documents(
            query=query,
            store_id=store_id,
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
def search_bbs_posts(query: str = "", days: int = 30) -> str:
    """
    全店舗の掲示板の投稿を検索し、各投稿のコメント（議論の流れ）も一緒に返します。
    本部からのお知らせや他店舗の投稿も含めて検索できます。

    Args:
        query: 検索クエリ（例: "シフト調整", "設備トラブル", "営業時間"）
        days: 検索対象日数（デフォルト: 30日）

    Returns:
        検索結果のJSON文字列（投稿とそのコメント一覧を含む）
    """
    try:
        from ai_features.services.core_services import VectorSearchService, QueryClassifier
        from bbs.models import BBSPost
        from datetime import date, timedelta

        # クエリの性質に応じてTop-K値を決定
        top_k = QueryClassifier.classify_and_get_top_k(query)

        # 日付フィルタ
        date_from = (date.today() - timedelta(days=days)).isoformat()

        # ベクトル検索実行（全店舗対象、store_id=None）
        search_results = VectorSearchService.search_documents(
            query=query,
            store_id=None,  # 全店舗検索
            source_types=['bbs_post'],
            filters={'date_from': date_from},
            top_k=top_k
        )

        # 結果を整形（スレッド単位）
        formatted_results = []
        for item in search_results:
            metadata = item.get('metadata', {})
            post_id = item.get('source_id')

            # 投稿のコメントをDBから取得
            comments_data = []
            best_answer = None
            store_name = metadata.get('store_name', '不明')
            try:
                post = BBSPost.objects.select_related('store').prefetch_related('comments__user').get(post_id=post_id)
                store_name = post.store.store_name if post.store else '不明'
                for comment in post.comments.all().order_by('created_at'):
                    comment_info = {
                        "author": comment.user.email if comment.user else "不明",
                        "content": comment.content,
                        "date": str(comment.created_at.date()),
                        "is_best_answer": comment.is_best_answer
                    }
                    comments_data.append(comment_info)
                    if comment.is_best_answer:
                        best_answer = comment.content
            except BBSPost.DoesNotExist:
                pass

            formatted_results.append({
                "date": metadata.get('date', '不明'),
                "store_name": store_name,
                "title": metadata.get('title', '不明'),
                "author": metadata.get('author_name', '不明'),
                "category": metadata.get('category', '未分類'),
                "content": item.get('content', ''),
                "similarity": round(float(item.get('similarity', 0)), 3),
                "comment_count": len(comments_data),
                "comments": comments_data,
                "best_answer": best_answer,
                "has_conclusion": best_answer is not None
            })

        result = {
            "status": "success",
            "query": query,
            "scope": "全店舗",
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
def search_bbs_by_keyword(keyword: str, days: int = 60) -> str:
    """
    全店舗の掲示板をキーワードで直接検索します（DB検索）。
    ベクトル検索ではなく、タイトル・内容に含まれるキーワードで確実に検索します。
    本部からのお知らせや他店舗の投稿も含めて検索できます。

    When to use this tool:
    - When looking for posts containing specific words (営業時間, シフト, 休み, etc.)
    - When vector search (search_bbs_posts) returns no results but user insists data exists
    - When searching for announcements or notices (お知らせ, 連絡, 報告)
    - Keywords: ○○について, ○○の投稿, ○○が書いてある

    Args:
        keyword: 検索キーワード（タイトルまたは内容に含まれる単語）
        days: 検索対象日数（デフォルト: 60日）

    Returns:
        キーワードを含む投稿とそのコメント一覧
    """
    try:
        from bbs.models import BBSPost
        from django.db.models import Q
        from datetime import date, timedelta

        end_date = date.today()
        start_date = end_date - timedelta(days=days)

        # デバッグログ
        logger.info(f"[search_bbs_by_keyword] keyword={keyword}, days={days}, start_date={start_date}, end_date={end_date}")

        # まず全投稿数を確認
        total_posts = BBSPost.objects.count()
        logger.info(f"[search_bbs_by_keyword] Total posts in DB: {total_posts}")

        # 日付範囲内の投稿数
        date_filtered = BBSPost.objects.filter(
            created_at__date__gte=start_date,
            created_at__date__lte=end_date
        ).count()
        logger.info(f"[search_bbs_by_keyword] Posts in date range: {date_filtered}")

        # キーワードでDB直接検索（全店舗対象、タイトルまたは内容に含まれる）
        posts = BBSPost.objects.filter(
            created_at__date__gte=start_date,
            created_at__date__lte=end_date
        ).filter(
            Q(title__icontains=keyword) | Q(content__icontains=keyword)
        ).select_related('store').prefetch_related(
            'comments__user', 'user'
        ).order_by('-created_at')[:20]

        logger.info(f"[search_bbs_by_keyword] Posts matching keyword: {len(posts)}")

        # コメント内にキーワードがある投稿も検索（全店舗）
        from bbs.models import BBSComment
        comment_post_ids = BBSComment.objects.filter(
            created_at__date__gte=start_date,
            created_at__date__lte=end_date,
            content__icontains=keyword
        ).values_list('post_id', flat=True).distinct()

        # コメントでヒットした投稿も追加
        comment_posts = BBSPost.objects.filter(
            post_id__in=comment_post_ids
        ).exclude(
            post_id__in=[p.post_id for p in posts]
        ).select_related('store').prefetch_related(
            'comments__user', 'user'
        ).order_by('-created_at')[:10]

        # 結果を整形
        formatted_results = []

        def format_post(post, match_type):
            comments_data = []
            best_answer = None
            for comment in post.comments.all().order_by('created_at'):
                comment_info = {
                    "author": comment.user.email if comment.user else "不明",
                    "content": comment.content,
                    "date": str(comment.created_at.date()),
                    "is_best_answer": comment.is_best_answer,
                    "contains_keyword": keyword.lower() in comment.content.lower()
                }
                comments_data.append(comment_info)
                if comment.is_best_answer:
                    best_answer = comment.content

            return {
                "date": str(post.created_at.date()),
                "store_name": post.store.store_name if post.store else "不明",
                "title": post.title,
                "author": post.user.email if post.user else "不明",
                "genre": post.genre,
                "content": post.content,
                "match_type": match_type,
                "comment_count": len(comments_data),
                "comments": comments_data,
                "best_answer": best_answer,
                "has_conclusion": best_answer is not None
            }

        # 投稿本文でヒットしたもの
        for post in posts:
            formatted_results.append(format_post(post, "タイトル/本文"))

        # コメントでヒットしたもの
        for post in comment_posts:
            formatted_results.append(format_post(post, "コメント"))

        if not formatted_results:
            return json.dumps({
                "status": "no_data",
                "message": f"「{keyword}」を含む掲示板投稿が見つかりませんでした。",
                "keyword": keyword,
                "scope": "全店舗",
                "days": days
            }, ensure_ascii=False)

        result = {
            "status": "success",
            "keyword": keyword,
            "scope": "全店舗",
            "days": days,
            "results": formatted_results,
            "total": len(formatted_results)
        }

        return json.dumps(result, ensure_ascii=False, indent=2)

    except Exception as e:
        logger.error(f"Error in search_bbs_by_keyword: {e}", exc_info=True)
        return json.dumps({
            "status": "error",
            "message": f"キーワード検索エラー: {str(e)}"
        }, ensure_ascii=False)


@tool
def search_bbs_posts_my_store(query: str = "", store_id: int = 0, days: int = 30) -> str:
    """
    自店舗の掲示板の投稿のみを検索します。自店舗内での議論やできごとを確認できます。

    Args:
        query: 検索クエリ（例: "シフト調整", "設備トラブル"）
        store_id: 店舗ID
        days: 検索対象日数（デフォルト: 30日）

    Returns:
        自店舗の投稿とそのコメント一覧
    """
    try:
        from ai_features.services.core_services import VectorSearchService, QueryClassifier
        from bbs.models import BBSPost
        from datetime import date, timedelta

        top_k = QueryClassifier.classify_and_get_top_k(query)
        date_from = (date.today() - timedelta(days=days)).isoformat()

        # 自店舗のみベクトル検索
        search_results = VectorSearchService.search_documents(
            query=query,
            store_id=store_id,  # 自店舗のみ
            source_types=['bbs_post'],
            filters={'date_from': date_from},
            top_k=top_k
        )

        formatted_results = []
        for item in search_results:
            metadata = item.get('metadata', {})
            post_id = item.get('source_id')

            comments_data = []
            best_answer = None
            try:
                post = BBSPost.objects.prefetch_related('comments__user').get(post_id=post_id)
                for comment in post.comments.all().order_by('created_at'):
                    comment_info = {
                        "author": comment.user.email if comment.user else "不明",
                        "content": comment.content,
                        "date": str(comment.created_at.date()),
                        "is_best_answer": comment.is_best_answer
                    }
                    comments_data.append(comment_info)
                    if comment.is_best_answer:
                        best_answer = comment.content
            except BBSPost.DoesNotExist:
                pass

            formatted_results.append({
                "date": metadata.get('date', '不明'),
                "title": metadata.get('title', '不明'),
                "author": metadata.get('author_name', '不明'),
                "category": metadata.get('category', '未分類'),
                "content": item.get('content', ''),
                "similarity": round(float(item.get('similarity', 0)), 3),
                "comment_count": len(comments_data),
                "comments": comments_data,
                "best_answer": best_answer,
                "has_conclusion": best_answer is not None
            })

        result = {
            "status": "success",
            "query": query,
            "scope": "自店舗",
            "store_id": store_id,
            "days": days,
            "results": formatted_results,
            "total": len(formatted_results)
        }

        return json.dumps(result, ensure_ascii=False, indent=2)

    except Exception as e:
        logger.error(f"Error in search_bbs_posts_my_store: {e}", exc_info=True)
        return json.dumps({
            "status": "error",
            "message": f"検索エラー: {str(e)}"
        }, ensure_ascii=False)


@tool
def search_bbs_by_keyword_my_store(keyword: str, store_id: int = 0, days: int = 60) -> str:
    """
    自店舗の掲示板をキーワードで検索します（DB検索）。自店舗内の投稿のみを対象とします。

    Args:
        keyword: 検索キーワード（タイトルまたは内容に含まれる単語）
        store_id: 店舗ID
        days: 検索対象日数（デフォルト: 60日）

    Returns:
        自店舗でキーワードを含む投稿とそのコメント一覧
    """
    try:
        from bbs.models import BBSPost, BBSComment
        from django.db.models import Q
        from datetime import date, timedelta

        end_date = date.today()
        start_date = end_date - timedelta(days=days)

        # 自店舗のみキーワード検索
        posts = BBSPost.objects.filter(
            store_id=store_id,
            created_at__date__gte=start_date,
            created_at__date__lte=end_date
        ).filter(
            Q(title__icontains=keyword) | Q(content__icontains=keyword)
        ).prefetch_related(
            'comments__user', 'user'
        ).order_by('-created_at')[:20]

        # コメント内検索も自店舗のみ
        comment_post_ids = BBSComment.objects.filter(
            post__store_id=store_id,
            created_at__date__gte=start_date,
            created_at__date__lte=end_date,
            content__icontains=keyword
        ).values_list('post_id', flat=True).distinct()

        comment_posts = BBSPost.objects.filter(
            post_id__in=comment_post_ids
        ).exclude(
            post_id__in=[p.post_id for p in posts]
        ).prefetch_related(
            'comments__user', 'user'
        ).order_by('-created_at')[:10]

        formatted_results = []

        def format_post(post, match_type):
            comments_data = []
            best_answer = None
            for comment in post.comments.all().order_by('created_at'):
                comment_info = {
                    "author": comment.user.email if comment.user else "不明",
                    "content": comment.content,
                    "date": str(comment.created_at.date()),
                    "is_best_answer": comment.is_best_answer,
                    "contains_keyword": keyword.lower() in comment.content.lower()
                }
                comments_data.append(comment_info)
                if comment.is_best_answer:
                    best_answer = comment.content

            return {
                "date": str(post.created_at.date()),
                "title": post.title,
                "author": post.user.email if post.user else "不明",
                "genre": post.genre,
                "content": post.content,
                "match_type": match_type,
                "comment_count": len(comments_data),
                "comments": comments_data,
                "best_answer": best_answer,
                "has_conclusion": best_answer is not None
            }

        for post in posts:
            formatted_results.append(format_post(post, "タイトル/本文"))

        for post in comment_posts:
            formatted_results.append(format_post(post, "コメント"))

        if not formatted_results:
            return json.dumps({
                "status": "no_data",
                "message": f"自店舗で「{keyword}」を含む掲示板投稿が見つかりませんでした。",
                "keyword": keyword,
                "scope": "自店舗",
                "days": days
            }, ensure_ascii=False)

        result = {
            "status": "success",
            "keyword": keyword,
            "scope": "自店舗",
            "store_id": store_id,
            "days": days,
            "results": formatted_results,
            "total": len(formatted_results)
        }

        return json.dumps(result, ensure_ascii=False, indent=2)

    except Exception as e:
        logger.error(f"Error in search_bbs_by_keyword_my_store: {e}", exc_info=True)
        return json.dumps({
            "status": "error",
            "message": f"キーワード検索エラー: {str(e)}"
        }, ensure_ascii=False)


@tool
def search_manual(query: str = "", category: Optional[str] = None) -> str:
    """
    業務マニュアル・ガイドライン・手順書を検索します。全店舗共通のナレッジベースです。

    Args:
        query: 検索クエリ（例: "クレーム対応手順", "食中毒予防"）
        category: カテゴリフィルタ（例: "衛生管理", "接客", "調理"）省略可能

    Returns:
        検索結果のJSON文字列
    """
    try:
        from ai_features.services.core_services import VectorSearchService

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


@tool
def search_by_genre(query: str, store_id: int, genre: str, days: int = 60) -> str:
    """
    Search daily reports filtered by specific genre (claim/praise/accident/report/other).

    This tool combines vector search with genre filtering for more precise results.

    When to use this tool:
    - When user specifically wants to search within a particular genre
    - When narrowing search to only claims (クレームのみ), only praise (賞賛のみ), etc.
    - When the genre is explicitly mentioned in the query
    - Keywords: クレームだけ, 賞賛のみ, 事故だけ, 報告のみ

    Args:
        query: Search query
        store_id: Store ID
        genre: Genre filter (claim/praise/accident/report/other)
        days: Search period in days (default: 60)

    Returns:
        JSON string containing filtered search results
    """
    try:
        from reports.models import DailyReport
        from django.db import models
        from datetime import date, timedelta

        # ジャンルの妥当性チェック
        valid_genres = ['claim', 'praise', 'accident', 'report', 'other']
        if genre not in valid_genres:
            return json.dumps({
                "status": "error",
                "message": f"無効なジャンルです。有効な値: {', '.join(valid_genres)}"
            }, ensure_ascii=False)

        end_date = date.today()
        start_date = end_date - timedelta(days=days)

        # ジャンルで絞り込んだ日報を取得
        reports = DailyReport.objects.filter(
            store_id=store_id,
            genre=genre,
            date__gte=start_date,
            date__lte=end_date
        ).order_by('-date')

        # クエリでさらに絞り込み（タイトルまたは内容に含まれる）
        if query:
            reports = reports.filter(
                models.Q(title__icontains=query) | models.Q(content__icontains=query)
            )

        # 結果を整形
        formatted_results = []
        for report in reports[:20]:  # 最大20件
            formatted_results.append({
                "date": str(report.date),
                "genre": dict(DailyReport.GENRE_CHOICES).get(report.genre, report.genre),
                "location": dict(DailyReport.LOCATION_CHOICES).get(report.location, report.location),
                "title": report.title,
                "content": report.content[:200],  # 最大200文字
                "author": report.user.user_id if report.user else "不明"
            })

        result = {
            "status": "success",
            "query": query,
            "store_id": store_id,
            "genre": genre,
            "days": days,
            "results": formatted_results,
            "total": len(formatted_results)
        }

        return json.dumps(result, ensure_ascii=False, indent=2)

    except Exception as e:
        logger.error(f"Error in search_by_genre: {e}", exc_info=True)
        return json.dumps({
            "status": "error",
            "message": f"ジャンル検索エラー: {str(e)}"
        }, ensure_ascii=False)


@tool
def search_by_location(query: str, store_id: int, location: str, days: int = 60) -> str:
    """
    Search daily reports filtered by specific location (kitchen/hall/cashier/toilet/other).

    This tool helps identify location-specific issues and patterns.

    When to use this tool:
    - When user wants to search within a specific location
    - When analyzing problems in a particular area (キッチンだけ, ホールのみ, etc.)
    - When the location is explicitly mentioned in the query
    - Keywords: キッチンだけ, ホールのみ, レジの, トイレの

    Args:
        query: Search query
        store_id: Store ID
        location: Location filter (kitchen/hall/cashier/toilet/other)
        days: Search period in days (default: 60)

    Returns:
        JSON string containing location-filtered search results
    """
    try:
        from reports.models import DailyReport
        from django.db import models
        from datetime import date, timedelta

        # 場所の妥当性チェック
        valid_locations = ['kitchen', 'hall', 'cashier', 'toilet', 'other']
        if location not in valid_locations:
            return json.dumps({
                "status": "error",
                "message": f"無効な場所です。有効な値: {', '.join(valid_locations)}"
            }, ensure_ascii=False)

        end_date = date.today()
        start_date = end_date - timedelta(days=days)

        # 場所で絞り込んだ日報を取得
        reports = DailyReport.objects.filter(
            store_id=store_id,
            location=location,
            date__gte=start_date,
            date__lte=end_date
        ).order_by('-date')

        # クエリでさらに絞り込み
        if query:
            reports = reports.filter(
                models.Q(title__icontains=query) | models.Q(content__icontains=query)
            )

        # 結果を整形
        formatted_results = []
        for report in reports[:20]:  # 最大20件
            formatted_results.append({
                "date": str(report.date),
                "genre": dict(DailyReport.GENRE_CHOICES).get(report.genre, report.genre),
                "location": dict(DailyReport.LOCATION_CHOICES).get(report.location, report.location),
                "title": report.title,
                "content": report.content[:200],
                "author": report.user.user_id if report.user else "不明"
            })

        result = {
            "status": "success",
            "query": query,
            "store_id": store_id,
            "location": location,
            "days": days,
            "results": formatted_results,
            "total": len(formatted_results)
        }

        return json.dumps(result, ensure_ascii=False, indent=2)

    except Exception as e:
        logger.error(f"Error in search_by_location: {e}", exc_info=True)
        return json.dumps({
            "status": "error",
            "message": f"場所検索エラー: {str(e)}"
        }, ensure_ascii=False)


# ============================================================
# 全店舗検索ツール（All Stores）
# ============================================================

@tool
def search_daily_reports_all_stores(query: str = "", days: int = 60) -> str:
    """
    全店舗の日報データを検索します。他店舗の事例やベストプラクティスを参考にできます。

    When to use this tool:
    - When user wants to see examples from other stores (他店舗の事例, 他の店の状況)
    - When looking for best practices across all stores (全店舗, ベストプラクティス)
    - When comparing issues across multiple stores

    Args:
        query: 検索クエリ（例: "クレーム対応", "接客改善"）
        days: 検索対象日数（デフォルト: 60日）

    Returns:
        全店舗の検索結果のJSON文字列
    """
    try:
        from ai_features.services.core_services import VectorSearchService, QueryClassifier
        from datetime import date, timedelta

        # クエリの性質に応じてTop-K値を決定
        top_k = QueryClassifier.classify_and_get_top_k(query)

        # 日付フィルタ
        date_from = (date.today() - timedelta(days=days)).isoformat()

        # ベクトル検索実行（全店舗）
        search_results = VectorSearchService.search_documents(
            query=query,
            store_id=None,  # 全店舗
            source_types=['daily_report'],
            filters={'date_from': date_from},
            top_k=top_k * 2  # 全店舗なので件数を増やす
        )

        # 結果を整形
        formatted_results = []
        for item in search_results:
            metadata = item.get('metadata', {})
            formatted_results.append({
                "date": metadata.get('date', '不明'),
                "type": "日報",
                "store_name": metadata.get('store_name', '不明'),
                "content": item.get('content', ''),
                "similarity": round(float(item.get('similarity', 0)), 3),
                "has_claim": metadata.get('has_claim', False),
                "has_praise": metadata.get('has_praise', False),
                "has_accident": metadata.get('has_accident', False),
            })

        result = {
            "status": "success",
            "query": query,
            "scope": "全店舗",
            "days": days,
            "top_k": top_k * 2,
            "results": formatted_results,
            "total": len(formatted_results)
        }

        return json.dumps(result, ensure_ascii=False, indent=2)

    except Exception as e:
        logger.error(f"Error in search_daily_reports_all_stores: {e}", exc_info=True)
        return json.dumps({
            "status": "error",
            "message": f"全店舗検索エラー: {str(e)}"
        }, ensure_ascii=False)


@tool
def search_bbs_posts_all_stores(query: str = "", days: int = 30) -> str:
    """
    全店舗の掲示板投稿を検索し、各投稿のコメント（議論の流れ）も一緒に返します。
    他店舗での議論や解決策を参考にできます。

    When to use this tool:
    - When user wants to see discussions from other stores (他店の意見, 他店舗の議論)
    - When looking for solutions implemented in other stores
    - When sharing knowledge across stores

    Args:
        query: 検索クエリ（例: "シフト改善", "メニュー工夫"）
        days: 検索対象日数（デフォルト: 30日）

    Returns:
        全店舗の検索結果のJSON文字列（投稿とそのコメント一覧を含む）
    """
    try:
        from ai_features.services.core_services import VectorSearchService, QueryClassifier
        from bbs.models import BBSPost
        from datetime import date, timedelta

        # クエリの性質に応じてTop-K値を決定
        top_k = QueryClassifier.classify_and_get_top_k(query)

        # 日付フィルタ
        date_from = (date.today() - timedelta(days=days)).isoformat()

        # ベクトル検索実行（全店舗、投稿のみ検索）
        search_results = VectorSearchService.search_documents(
            query=query,
            store_id=None,  # 全店舗
            source_types=['bbs_post'],
            filters={'date_from': date_from},
            top_k=top_k * 2  # 全店舗なので件数を増やす
        )

        # 結果を整形（スレッド単位）
        formatted_results = []
        for item in search_results:
            metadata = item.get('metadata', {})
            post_id = item.get('source_id')

            # 投稿のコメントをDBから取得
            comments_data = []
            best_answer = None
            try:
                post = BBSPost.objects.prefetch_related('comments__user').get(post_id=post_id)
                for comment in post.comments.all().order_by('created_at'):
                    comment_info = {
                        "author": comment.user.email if comment.user else "不明",
                        "content": comment.content,
                        "date": str(comment.created_at.date()),
                        "is_best_answer": comment.is_best_answer
                    }
                    comments_data.append(comment_info)
                    if comment.is_best_answer:
                        best_answer = comment.content
            except BBSPost.DoesNotExist:
                pass

            formatted_results.append({
                "date": metadata.get('date', '不明'),
                "store_name": metadata.get('store_name', '不明'),
                "title": metadata.get('title', '不明'),
                "author": metadata.get('author_name', '不明'),
                "category": metadata.get('category', '未分類'),
                "content": item.get('content', ''),
                "similarity": round(float(item.get('similarity', 0)), 3),
                "comment_count": len(comments_data),
                "comments": comments_data,
                "best_answer": best_answer,
                "has_conclusion": best_answer is not None
            })

        result = {
            "status": "success",
            "query": query,
            "scope": "全店舗",
            "days": days,
            "top_k": top_k * 2,
            "results": formatted_results,
            "total": len(formatted_results)
        }

        return json.dumps(result, ensure_ascii=False, indent=2)

    except Exception as e:
        logger.error(f"Error in search_bbs_posts_all_stores: {e}", exc_info=True)
        return json.dumps({
            "status": "error",
            "message": f"全店舗掲示板検索エラー: {str(e)}"
        }, ensure_ascii=False)


@tool
def search_by_genre_all_stores(query: str, genre: str, days: int = 60) -> str:
    """
    全店舗の日報をジャンルで絞り込んで検索します。

    When to use this tool:
    - When user wants to search within a particular genre across all stores
    - When comparing how different stores handle the same genre of issues

    Args:
        query: 検索クエリ
        genre: ジャンルフィルタ (claim/praise/accident/report/other)
        days: 検索対象日数（デフォルト: 60日）

    Returns:
        全店舗のジャンル別検索結果のJSON文字列
    """
    try:
        from reports.models import DailyReport
        from django.db import models
        from datetime import date, timedelta

        # ジャンルの妥当性チェック
        valid_genres = ['claim', 'praise', 'accident', 'report', 'other']
        if genre not in valid_genres:
            return json.dumps({
                "status": "error",
                "message": f"無効なジャンルです。有効な値: {', '.join(valid_genres)}"
            }, ensure_ascii=False)

        end_date = date.today()
        start_date = end_date - timedelta(days=days)

        # 全店舗のジャンルで絞り込んだ日報を取得
        reports = DailyReport.objects.filter(
            genre=genre,
            date__gte=start_date,
            date__lte=end_date
        ).order_by('-date')

        # クエリでさらに絞り込み
        if query:
            reports = reports.filter(
                models.Q(title__icontains=query) | models.Q(content__icontains=query)
            )

        # 結果を整形
        formatted_results = []
        for report in reports[:30]:  # 全店舗なので30件
            formatted_results.append({
                "date": str(report.date),
                "store_name": report.store.store_name if report.store else "不明",
                "genre": dict(DailyReport.GENRE_CHOICES).get(report.genre, report.genre),
                "location": dict(DailyReport.LOCATION_CHOICES).get(report.location, report.location),
                "title": report.title,
                "content": report.content[:200],
                "author": report.user.user_id if report.user else "不明"
            })

        result = {
            "status": "success",
            "query": query,
            "scope": "全店舗",
            "genre": genre,
            "days": days,
            "results": formatted_results,
            "total": len(formatted_results)
        }

        return json.dumps(result, ensure_ascii=False, indent=2)

    except Exception as e:
        logger.error(f"Error in search_by_genre_all_stores: {e}", exc_info=True)
        return json.dumps({
            "status": "error",
            "message": f"全店舗ジャンル検索エラー: {str(e)}"
        }, ensure_ascii=False)


@tool
def search_by_location_all_stores(query: str, location: str, days: int = 60) -> str:
    """
    全店舗の日報を場所で絞り込んで検索します。

    When to use this tool:
    - When user wants to search within a specific location across all stores
    - When comparing location-specific issues between stores

    Args:
        query: 検索クエリ
        location: 場所フィルタ (kitchen/hall/cashier/toilet/other)
        days: 検索対象日数（デフォルト: 60日）

    Returns:
        全店舗の場所別検索結果のJSON文字列
    """
    try:
        from reports.models import DailyReport
        from django.db import models
        from datetime import date, timedelta

        # 場所の妥当性チェック
        valid_locations = ['kitchen', 'hall', 'cashier', 'toilet', 'other']
        if location not in valid_locations:
            return json.dumps({
                "status": "error",
                "message": f"無効な場所です。有効な値: {', '.join(valid_locations)}"
            }, ensure_ascii=False)

        end_date = date.today()
        start_date = end_date - timedelta(days=days)

        # 全店舗の場所で絞り込んだ日報を取得
        reports = DailyReport.objects.filter(
            location=location,
            date__gte=start_date,
            date__lte=end_date
        ).order_by('-date')

        # クエリでさらに絞り込み
        if query:
            reports = reports.filter(
                models.Q(title__icontains=query) | models.Q(content__icontains=query)
            )

        # 結果を整形
        formatted_results = []
        for report in reports[:30]:  # 全店舗なので30件
            formatted_results.append({
                "date": str(report.date),
                "store_name": report.store.store_name if report.store else "不明",
                "genre": dict(DailyReport.GENRE_CHOICES).get(report.genre, report.genre),
                "location": dict(DailyReport.LOCATION_CHOICES).get(report.location, report.location),
                "title": report.title,
                "content": report.content[:200],
                "author": report.user.user_id if report.user else "不明"
            })

        result = {
            "status": "success",
            "query": query,
            "scope": "全店舗",
            "location": location,
            "days": days,
            "results": formatted_results,
            "total": len(formatted_results)
        }

        return json.dumps(result, ensure_ascii=False, indent=2)

    except Exception as e:
        logger.error(f"Error in search_by_location_all_stores: {e}", exc_info=True)
        return json.dumps({
            "status": "error",
            "message": f"全店舗場所検索エラー: {str(e)}"
        }, ensure_ascii=False)
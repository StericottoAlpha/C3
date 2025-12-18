"""
統計・分析ツール（store_id引数版）
LangChain @tool デコレータを使用
"""
import logging
import json
from typing import Optional
from datetime import datetime, timedelta

from langchain_core.tools import tool

logger = logging.getLogger(__name__)

@tool
def get_claim_statistics(store_id: int, days: int = 30) -> str:
    """
    クレーム統計を取得します。指定期間のクレーム件数、内容の傾向を分析します。
    """
    try:
        from reports.models import DailyReport
        from django.db.models import Count, Q
        from datetime import datetime, timedelta
        import json

        end_date = datetime.now().date()
        start_date = end_date - timedelta(days=days)

        # 期間内全データ
        queryset = DailyReport.objects.filter(
            store_id=store_id,
            date__gte=start_date,
            date__lte=end_date
        )

        total_reports = queryset.count()

        # 🎯 クレームは genre='claim'
        #    内容（content）が空でないものに限定
        claim_reports = queryset.filter(
            genre='claim',
            content__isnull=False
        ).exclude(content='')

        claim_count = claim_reports.count()
        claim_rate = f"{(claim_count / total_reports * 100):.1f}%" if total_reports else "0%"

        # 日別トレンド（最近7日）- DBで集計
        recent_days = min(7, days)
        recent_start = end_date - timedelta(days=recent_days - 1)

        daily_trend_qs = claim_reports.filter(
            date__gte=recent_start
        ).values('date').annotate(
            count=Count('report_id')
        ).order_by('-date')

        # 日付をキーにした辞書を作成
        trend_dict = {item['date']: item['count'] for item in daily_trend_qs}

        # 全日付を網羅（データがない日は0件）
        daily_trend = []
        for i in range(recent_days):
            target_date = end_date - timedelta(days=i)
            daily_trend.append({
                "date": str(target_date),
                "count": trend_dict.get(target_date, 0)
            })

        # カテゴリ別（location）
        claim_by_genre = claim_reports.values('location').annotate(
            count=Count('report_id')
        ).order_by('-count')[:5]

        top_categories = [
            {"category": item['location'], "count": item['count']}
            for item in claim_by_genre
        ]

        result = {
            "status": "success",
            "store_id": store_id,
            "period_days": days,
            "summary": {
                "total_reports": total_reports,
                "claim_count": claim_count,
                "claim_rate": claim_rate
            },
            "daily_trend": daily_trend,
            "top_categories": top_categories
        }

        return json.dumps(result, ensure_ascii=False, indent=2)

    except Exception as e:
        logger.error(f"Error in get_claim_statistics: {e}", exc_info=True)
        return json.dumps({
            "status": "error",
            "message": f"統計取得エラー: {str(e)}"
        }, ensure_ascii=False)



@tool
def get_sales_trend(store_id: int, days: int = 30) -> str:
    """
    Get sales trend data including total, average, customer count, daily trends, and weekly comparison.

    This tool retrieves structured sales performance data from the database and provides statistical analysis.

    When to use this tool:
    - When user asks about sales amounts, revenue, or sales performance (売上)
    - When checking trends or patterns in sales data
    - When comparing with previous week/month sales
    - When analyzing customer count (客数) or average per customer (客単価)
    - Keywords: 売上, 売り上げ, 収益, 客数, 客単価

    Args:
        store_id: Store ID
        days: Number of days to aggregate (default: 30)

    Returns:
        JSON string containing sales trend data with summary, daily breakdown, and weekly comparison
    """
    try:
        from reports.models import StoreDailyPerformance
        from django.db.models import Sum, Avg, Max, Min, Count

        end_date = datetime.now().date()
        start_date = end_date - timedelta(days=days)

        # 期間内のパフォーマンスデータを取得
        queryset = StoreDailyPerformance.objects.filter(
            store_id=store_id,
            date__gte=start_date,
            date__lte=end_date
        )

        # 集計データが存在するか確認
        if not queryset.exists():
            return json.dumps({
                "status": "no_data",
                "message": f"指定期間（過去{days}日間）の売上データが登録されていません。"
            }, ensure_ascii=False)

        # 基本統計
        aggregates = queryset.aggregate(
            total_sales=Sum('sales_amount'),
            avg_sales=Avg('sales_amount'),
            max_sales=Max('sales_amount'),
            min_sales=Min('sales_amount'),
            total_customers=Sum('customer_count'),
            avg_customers=Avg('customer_count'),
            data_count=Count('performance_id')
        )

        # 日別トレンド（最新7日分）- DBで一括取得
        recent_days = min(7, days)
        recent_start = end_date - timedelta(days=recent_days - 1)

        daily_records = queryset.filter(
            date__gte=recent_start
        ).order_by('-date').values('date', 'sales_amount', 'customer_count')

        daily_data = [
            {
                "date": str(record['date']),
                "sales": record['sales_amount'],
                "customers": record['customer_count'],
                "avg_per_customer": round(record['sales_amount'] / record['customer_count'], 0)
                    if record['customer_count'] > 0 else 0
            }
            for record in daily_records
        ]

        # 週次比較（過去2週間）
        week_comparison = None
        if days >= 14:
            this_week_start = end_date - timedelta(days=6)
            last_week_start = end_date - timedelta(days=13)
            last_week_end = end_date - timedelta(days=7)

            this_week_sales = queryset.filter(
                date__gte=this_week_start, date__lte=end_date
            ).aggregate(total=Sum('sales_amount'))['total'] or 0

            last_week_sales = queryset.filter(
                date__gte=last_week_start, date__lte=last_week_end
            ).aggregate(total=Sum('sales_amount'))['total'] or 0

            if last_week_sales > 0:
                change_rate = (this_week_sales - last_week_sales) / last_week_sales * 100
                week_comparison = {
                    "this_week": this_week_sales,
                    "last_week": last_week_sales,
                    "change_amount": this_week_sales - last_week_sales,
                    "change_rate": f"{change_rate:.1f}%"
                }

        # 客単価計算
        total_sales = aggregates['total_sales'] or 0
        total_customers = aggregates['total_customers'] or 0
        avg_per_customer = round(total_sales / total_customers, 0) if total_customers > 0 else 0

        result = {
            "status": "success",
            "store_id": store_id,
            "period_days": days,
            "summary": {
                "data_count": aggregates['data_count'],
                "total_sales": total_sales,
                "avg_sales": round(aggregates['avg_sales'], 0) if aggregates['avg_sales'] else 0,
                "max_sales": aggregates['max_sales'] or 0,
                "min_sales": aggregates['min_sales'] or 0,
                "total_customers": total_customers,
                "avg_customers": round(aggregates['avg_customers'], 1) if aggregates['avg_customers'] else 0,
                "avg_per_customer": avg_per_customer
            },
            "daily_trend": daily_data,
            "week_comparison": week_comparison
        }

        return json.dumps(result, ensure_ascii=False, indent=2)

    except Exception as e:
        logger.error(f"Error in get_sales_trend: {e}", exc_info=True)
        return json.dumps({
            "status": "error",
            "message": f"売上推移取得エラー: {str(e)}"
        }, ensure_ascii=False)


@tool
def get_cash_difference_analysis(store_id: int, days: int = 30) -> str:
    """
    Get cash difference (register discrepancy) analysis including total amount, frequency, and plus/minus breakdown.

    This tool analyzes cash register differences to identify cash management issues and patterns.

    When to use this tool:
    - When user asks about cash differences, register discrepancies (違算, 現金過不足)
    - When checking cash management accuracy
    - When analyzing register closing issues (レジ締め)
    - Keywords: 違算, 現金過不足, レジ差異, 金額差異, 現金管理

    Args:
        store_id: Store ID
        days: Number of days to aggregate (default: 30)

    Returns:
        JSON string containing cash difference analysis with totals, frequency, and daily breakdown
    """
    try:
        from reports.models import StoreDailyPerformance
        from django.db.models import Sum, Avg, Max, Min, Count, Q

        end_date = datetime.now().date()
        start_date = end_date - timedelta(days=days)

        # 期間内のパフォーマンスデータを取得
        queryset = StoreDailyPerformance.objects.filter(
            store_id=store_id,
            date__gte=start_date,
            date__lte=end_date
        )

        # データが存在するか確認
        if not queryset.exists():
            return json.dumps({
                "status": "no_data",
                "message": f"指定期間（過去{days}日間）の現金過不足データが登録されていません。"
            }, ensure_ascii=False)

        # 基本統計
        aggregates = queryset.aggregate(
            total_difference=Sum('cash_difference'),
            avg_difference=Avg('cash_difference'),
            max_difference=Max('cash_difference'),
            min_difference=Min('cash_difference'),
            data_count=Count('performance_id')
        )

        # プラス/マイナスの内訳
        plus_records = queryset.filter(cash_difference__gt=0)
        minus_records = queryset.filter(cash_difference__lt=0)
        zero_records = queryset.filter(cash_difference=0)

        plus_stats = plus_records.aggregate(
            count=Count('performance_id'),
            total=Sum('cash_difference'),
            avg=Avg('cash_difference')
        )

        minus_stats = minus_records.aggregate(
            count=Count('performance_id'),
            total=Sum('cash_difference'),
            avg=Avg('cash_difference')
        )

        # 違算発生日の分析
        difference_occurred_count = queryset.exclude(cash_difference=0).count()
        difference_rate = f"{(difference_occurred_count / aggregates['data_count'] * 100):.1f}%" if aggregates['data_count'] > 0 else "0%"

        # 日別トレンド（最近7日間で違算があった日）- DBで一括取得
        recent_days = min(7, days)
        recent_start = end_date - timedelta(days=recent_days - 1)

        daily_records = queryset.filter(
            date__gte=recent_start
        ).exclude(cash_difference=0).order_by('-date').values('date', 'cash_difference')

        daily_data = [
            {
                "date": str(record['date']),
                "difference": record['cash_difference'],
                "type": "プラス" if record['cash_difference'] > 0 else "マイナス"
            }
            for record in daily_records
        ]

        result = {
            "status": "success",
            "store_id": store_id,
            "period_days": days,
            "summary": {
                "data_count": aggregates['data_count'],
                "total_difference": aggregates['total_difference'] or 0,
                "avg_difference": round(aggregates['avg_difference'], 0) if aggregates['avg_difference'] else 0,
                "max_difference": aggregates['max_difference'] or 0,
                "min_difference": aggregates['min_difference'] or 0,
                "difference_occurred_count": difference_occurred_count,
                "difference_rate": difference_rate,
                "zero_count": zero_records.count()
            },
            "plus_minus_breakdown": {
                "plus": {
                    "count": plus_stats['count'] or 0,
                    "total": plus_stats['total'] or 0,
                    "avg": round(plus_stats['avg'], 0) if plus_stats['avg'] else 0
                },
                "minus": {
                    "count": minus_stats['count'] or 0,
                    "total": minus_stats['total'] or 0,
                    "avg": round(minus_stats['avg'], 0) if minus_stats['avg'] else 0
                }
            },
            "recent_differences": daily_data
        }

        return json.dumps(result, ensure_ascii=False, indent=2)

    except Exception as e:
        logger.error(f"Error in get_cash_difference_analysis: {e}", exc_info=True)
        return json.dumps({
            "status": "error",
            "message": f"現金過不足分析エラー: {str(e)}"
        }, ensure_ascii=False)


@tool
def get_report_statistics(store_id: int, days: int = 30) -> str:
    """
    Get daily report statistics including genre breakdown (claims, praise, accidents, reports) and location analysis.

    This tool provides an overview of daily report submission patterns and categorization trends.

    When to use this tool:
    - When user wants an overview of daily reports (日報の全体像)
    - When analyzing report submission frequency or patterns
    - When checking which genres (ジャンル) or locations (場所) are most common
    - Keywords: 日報統計, 報告件数, ジャンル別, 場所別

    Args:
        store_id: Store ID
        days: Number of days to aggregate (default: 30)

    Returns:
        JSON string containing report statistics with genre/location breakdown
    """
    try:
        from reports.models import DailyReport
        from django.db.models import Count

        end_date = datetime.now().date()
        start_date = end_date - timedelta(days=days)

        # 期間内の日報を取得
        queryset = DailyReport.objects.filter(
            store_id=store_id,
            date__gte=start_date,
            date__lte=end_date
        )

        total_reports = queryset.count()

        if total_reports == 0:
            return json.dumps({
                "status": "no_data",
                "message": f"指定期間（過去{days}日間）の日報データがありません。"
            }, ensure_ascii=False)

        # ジャンル別集計
        genre_breakdown = queryset.values('genre').annotate(
            count=Count('report_id')
        ).order_by('-count')

        genre_data = []
        for item in genre_breakdown:
            genre_display = dict(DailyReport.GENRE_CHOICES).get(item['genre'], item['genre'])
            percentage = (item['count'] / total_reports * 100) if total_reports > 0 else 0
            genre_data.append({
                "genre": item['genre'],
                "genre_display": genre_display,
                "count": item['count'],
                "percentage": f"{percentage:.1f}%"
            })

        # 場所別集計
        location_breakdown = queryset.values('location').annotate(
            count=Count('report_id')
        ).order_by('-count')

        location_data = []
        for item in location_breakdown:
            location_display = dict(DailyReport.LOCATION_CHOICES).get(item['location'], item['location'])
            percentage = (item['count'] / total_reports * 100) if total_reports > 0 else 0
            location_data.append({
                "location": item['location'],
                "location_display": location_display,
                "count": item['count'],
                "percentage": f"{percentage:.1f}%"
            })

        # 日別投稿頻度（最近7日間）- DBで集計
        recent_days = min(7, days)
        recent_start = end_date - timedelta(days=recent_days - 1)

        daily_submission_qs = queryset.filter(
            date__gte=recent_start
        ).values('date').annotate(
            count=Count('report_id')
        ).order_by('-date')

        # 日付をキーにした辞書を作成
        submission_dict = {item['date']: item['count'] for item in daily_submission_qs}

        # 全日付を網羅（データがない日は0件）
        daily_submission = []
        for i in range(recent_days):
            target_date = end_date - timedelta(days=i)
            daily_submission.append({
                "date": str(target_date),
                "count": submission_dict.get(target_date, 0)
            })

        result = {
            "status": "success",
            "store_id": store_id,
            "period_days": days,
            "summary": {
                "total_reports": total_reports,
                "avg_per_day": round(total_reports / days, 1)
            },
            "genre_breakdown": genre_data,
            "location_breakdown": location_data,
            "daily_submission": daily_submission
        }

        return json.dumps(result, ensure_ascii=False, indent=2)

    except Exception as e:
        logger.error(f"Error in get_report_statistics: {e}", exc_info=True)
        return json.dumps({
            "status": "error",
            "message": f"日報統計取得エラー: {str(e)}"
        }, ensure_ascii=False)


@tool
def get_monthly_goal_status(store_id: int) -> str:
    """
    Get monthly goal information including current month's goal, achievement rate, and past goal history.

    This tool helps track store goals and monitor progress toward targets.

    When to use this tool:
    - When user asks about monthly goals or targets (月次目標, 目標達成)
    - When checking goal achievement status (達成率)
    - When reviewing past goal performance
    - Keywords: 目標, 月次目標, 達成率, 目標達成

    Args:
        store_id: Store ID

    Returns:
        JSON string containing current goal status and historical data
    """
    try:
        from stores.models import MonthlyGoal

        current_date = datetime.now()
        current_year = current_date.year
        current_month = current_date.month

        # 今月の目標を取得
        current_goal = MonthlyGoal.objects.filter(
            store_id=store_id,
            year=current_year,
            month=current_month
        ).first()

        if not current_goal:
            return json.dumps({
                "status": "no_data",
                "message": f"{current_year}年{current_month}月の目標が設定されていません。"
            }, ensure_ascii=False)

        # 過去6ヶ月の目標履歴を取得
        past_goals = MonthlyGoal.objects.filter(
            store_id=store_id
        ).order_by('-year', '-month')[:6]

        past_goal_data = []
        for goal in past_goals:
            if goal.year == current_year and goal.month == current_month:
                continue  # 今月の目標は除外
            past_goal_data.append({
                "year": goal.year,
                "month": goal.month,
                "goal_text": goal.goal_text,
                "achievement_rate": goal.achievement_rate,
                "achievement_text": goal.achievement_text
            })

        result = {
            "status": "success",
            "store_id": store_id,
            "current_goal": {
                "year": current_goal.year,
                "month": current_goal.month,
                "goal_text": current_goal.goal_text,
                "achievement_rate": current_goal.achievement_rate,
                "achievement_text": current_goal.achievement_text
            },
            "past_goals": past_goal_data[:5]  # 最大5件の履歴
        }

        return json.dumps(result, ensure_ascii=False, indent=2)

    except Exception as e:
        logger.error(f"Error in get_monthly_goal_status: {e}", exc_info=True)
        return json.dumps({
            "status": "error",
            "message": f"月次目標取得エラー: {str(e)}"
        }, ensure_ascii=False)


@tool
def gather_topic_related_data(topic: str, store_id: int, days: int = 30) -> str:
    """
    Gather all related data about a specific topic from multiple sources (DATA COLLECTION ONLY).

    This tool performs comprehensive data retrieval across daily reports, BBS posts, and statistics.
    It does NOT analyze or interpret - it only collects and returns raw data for LLM analysis.

    When to use this tool:
    - When user asks for advice on a specific issue (問題についてアドバイス)
    - When analyzing a topic comprehensively (総合的な分析が必要)
    - When you need context from multiple sources
    - Keywords: について教えて, 分析して, アドバイス, 改善策

    Args:
        topic: Topic keyword (e.g., "クレーム", "売上", "接客", "事故")
        store_id: Store ID
        days: Search period in days (default: 30)

    Returns:
        JSON containing data from daily reports, BBS, and relevant statistics
    """
    try:
        from reports.models import DailyReport
        from bbs.models import BBSPost, BBSComment
        from django.db.models import Q, Count
        from datetime import datetime, timedelta

        end_date = datetime.now().date()
        start_date = end_date - timedelta(days=days)

        result = {
            "status": "success",
            "topic": topic,
            "store_id": store_id,
            "period_days": days,
            "data_sources": {}
        }

        # 1. 日報からの情報収集
        daily_reports = DailyReport.objects.filter(
            store_id=store_id,
            date__gte=start_date,
            date__lte=end_date
        ).filter(
            Q(title__icontains=topic) | Q(content__icontains=topic)
        ).order_by('-date')[:20]

        reports_data = []
        for report in daily_reports:
            reports_data.append({
                "date": str(report.date),
                "genre": dict(DailyReport.GENRE_CHOICES).get(report.genre, report.genre),
                "location": dict(DailyReport.LOCATION_CHOICES).get(report.location, report.location),
                "title": report.title,
                "content": report.content[:300],
                "author": report.user.user_id if report.user else "不明"
            })

        result["data_sources"]["daily_reports"] = {
            "count": len(reports_data),
            "items": reports_data
        }

        # 2. 掲示板からの情報収集 - prefetch_relatedでN+1クエリ解消
        from django.db.models import Prefetch

        bbs_posts = BBSPost.objects.filter(
            store_id=store_id,
            created_at__date__gte=start_date,
            created_at__date__lte=end_date
        ).filter(
            Q(title__icontains=topic) | Q(content__icontains=topic)
        ).prefetch_related(
            Prefetch(
                'comments',
                queryset=BBSComment.objects.select_related('user').order_by('created_at')[:5],
                to_attr='recent_comments'
            ),
            'user'  # 投稿者も一緒に取得
        ).order_by('-created_at')[:15]

        bbs_data = []
        for post in bbs_posts:
            # prefetchされたコメントを使用
            comment_list = [
                {
                    "author": comment.user.user_id if comment.user else "不明",
                    "content": comment.content[:200],
                    "created_at": comment.created_at.strftime("%Y-%m-%d %H:%M")
                }
                for comment in post.recent_comments
            ]

            bbs_data.append({
                "title": post.title,
                "content": post.content[:300],
                "author": post.user.user_id if post.user else "不明",
                "created_at": post.created_at.strftime("%Y-%m-%d"),
                "comment_count": post.comment_count,
                "comments": comment_list
            })

        result["data_sources"]["bbs_posts"] = {
            "count": len(bbs_data),
            "items": bbs_data
        }

        # 3. トピックに関連する統計（キーワードベース）
        topic_lower = topic.lower()
        statistics = {}

        if any(keyword in topic_lower for keyword in ["クレーム", "苦情", "claim"]):
            # クレーム統計を追加
            claim_reports = DailyReport.objects.filter(
                store_id=store_id,
                genre='claim',
                date__gte=start_date,
                date__lte=end_date
            )
            statistics["claim_count"] = claim_reports.count()
            statistics["claim_by_location"] = list(claim_reports.values('location').annotate(count=Count('report_id')).order_by('-count')[:3])

        if any(keyword in topic_lower for keyword in ["売上", "売り上げ", "sales", "revenue"]):
            # 売上統計を追加
            try:
                from reports.models import StoreDailyPerformance
                from django.db.models import Sum, Avg

                sales_data = StoreDailyPerformance.objects.filter(
                    store_id=store_id,
                    date__gte=start_date,
                    date__lte=end_date
                ).aggregate(
                    total=Sum('sales_amount'),
                    avg=Avg('sales_amount'),
                    count=Count('performance_id')
                )
                statistics["sales"] = {
                    "total": sales_data['total'] or 0,
                    "average": round(sales_data['avg'], 0) if sales_data['avg'] else 0,
                    "data_points": sales_data['count']
                }
            except Exception:
                pass

        if any(keyword in topic_lower for keyword in ["事故", "accident", "トラブル"]):
            # 事故統計を追加
            accident_reports = DailyReport.objects.filter(
                store_id=store_id,
                genre='accident',
                date__gte=start_date,
                date__lte=end_date
            )
            statistics["accident_count"] = accident_reports.count()

        result["data_sources"]["related_statistics"] = statistics

        return json.dumps(result, ensure_ascii=False, indent=2)

    except Exception as e:
        logger.error(f"Error in gather_topic_related_data: {e}", exc_info=True)
        return json.dumps({
            "status": "error",
            "message": f"情報収集エラー: {str(e)}"
        }, ensure_ascii=False)


@tool
def compare_periods(store_id: int, metric: str, period1_days: int = 7, period2_days: int = 14) -> str:
    """
    Compare metrics between two time periods (STATISTICAL CALCULATION ONLY).

    This tool retrieves data for two periods and calculates comparison metrics.
    It does NOT interpret results - interpretation is the LLM's responsibility.

    When to use this tool:
    - When user asks about changes or trends (変化、推移、比較)
    - When comparing current vs previous performance
    - When analyzing if situation improved or worsened
    - Keywords: 先週と比べて, 前回と比較, 増えた, 減った, 変化

    Args:
        store_id: Store ID
        metric: Metric to compare (sales/claims/accidents/reports/cash_difference)
        period1_days: Recent period days (default: 7 for last week)
        period2_days: Comparison period days (default: 14, means 8-14 days ago)

    Returns:
        JSON with side-by-side comparison and calculated change rates
    """
    try:
        from reports.models import DailyReport, StoreDailyPerformance
        from django.db.models import Sum, Avg, Count

        end_date = datetime.now().date()

        # Period 1: 直近（例: 過去7日間）
        period1_start = end_date - timedelta(days=period1_days)
        period1_end = end_date

        # Period 2: 比較対象（例: 8-14日前）
        period2_start = end_date - timedelta(days=period2_days)
        period2_end = end_date - timedelta(days=period1_days + 1)

        result = {
            "status": "success",
            "store_id": store_id,
            "metric": metric,
            "period1": {
                "label": f"直近{period1_days}日間",
                "start": str(period1_start),
                "end": str(period1_end)
            },
            "period2": {
                "label": f"{period1_days + 1}〜{period2_days}日前",
                "start": str(period2_start),
                "end": str(period2_end)
            }
        }

        if metric == "sales":
            # 売上比較
            p1_data = StoreDailyPerformance.objects.filter(
                store_id=store_id,
                date__gte=period1_start,
                date__lte=period1_end
            ).aggregate(
                total=Sum('sales_amount'),
                avg=Avg('sales_amount'),
                count=Count('performance_id')
            )

            p2_data = StoreDailyPerformance.objects.filter(
                store_id=store_id,
                date__gte=period2_start,
                date__lte=period2_end
            ).aggregate(
                total=Sum('sales_amount'),
                avg=Avg('sales_amount'),
                count=Count('performance_id')
            )

            p1_total = p1_data['total'] or 0
            p2_total = p2_data['total'] or 0
            change = p1_total - p2_total
            change_rate = (change / p2_total * 100) if p2_total > 0 else 0

            result["comparison"] = {
                "period1": {
                    "total": p1_total,
                    "average": round(p1_data['avg'], 0) if p1_data['avg'] else 0,
                    "data_points": p1_data['count']
                },
                "period2": {
                    "total": p2_total,
                    "average": round(p2_data['avg'], 0) if p2_data['avg'] else 0,
                    "data_points": p2_data['count']
                },
                "change": {
                    "absolute": change,
                    "rate": f"{change_rate:.1f}%",
                    "direction": "増加" if change > 0 else "減少" if change < 0 else "変化なし"
                }
            }

        elif metric == "claims":
            # クレーム比較
            p1_count = DailyReport.objects.filter(
                store_id=store_id,
                genre='claim',
                date__gte=period1_start,
                date__lte=period1_end
            ).count()

            p2_count = DailyReport.objects.filter(
                store_id=store_id,
                genre='claim',
                date__gte=period2_start,
                date__lte=period2_end
            ).count()

            change = p1_count - p2_count
            change_rate = (change / p2_count * 100) if p2_count > 0 else 0

            result["comparison"] = {
                "period1": {"count": p1_count},
                "period2": {"count": p2_count},
                "change": {
                    "absolute": change,
                    "rate": f"{change_rate:.1f}%",
                    "direction": "増加" if change > 0 else "減少" if change < 0 else "変化なし"
                }
            }

        elif metric == "accidents":
            # 事故比較
            p1_count = DailyReport.objects.filter(
                store_id=store_id,
                genre='accident',
                date__gte=period1_start,
                date__lte=period1_end
            ).count()

            p2_count = DailyReport.objects.filter(
                store_id=store_id,
                genre='accident',
                date__gte=period2_start,
                date__lte=period2_end
            ).count()

            change = p1_count - p2_count
            change_rate = (change / p2_count * 100) if p2_count > 0 else 0

            result["comparison"] = {
                "period1": {"count": p1_count},
                "period2": {"count": p2_count},
                "change": {
                    "absolute": change,
                    "rate": f"{change_rate:.1f}%",
                    "direction": "増加" if change > 0 else "減少" if change < 0 else "変化なし"
                }
            }

        elif metric == "reports":
            # 日報全体の比較
            p1_count = DailyReport.objects.filter(
                store_id=store_id,
                date__gte=period1_start,
                date__lte=period1_end
            ).count()

            p2_count = DailyReport.objects.filter(
                store_id=store_id,
                date__gte=period2_start,
                date__lte=period2_end
            ).count()

            change = p1_count - p2_count
            change_rate = (change / p2_count * 100) if p2_count > 0 else 0

            result["comparison"] = {
                "period1": {"count": p1_count},
                "period2": {"count": p2_count},
                "change": {
                    "absolute": change,
                    "rate": f"{change_rate:.1f}%",
                    "direction": "増加" if change > 0 else "減少" if change < 0 else "変化なし"
                }
            }

        elif metric == "cash_difference":
            # 現金過不足比較
            p1_data = StoreDailyPerformance.objects.filter(
                store_id=store_id,
                date__gte=period1_start,
                date__lte=period1_end
            ).aggregate(
                total=Sum('cash_difference'),
                avg=Avg('cash_difference'),
                count=Count('performance_id')
            )

            p2_data = StoreDailyPerformance.objects.filter(
                store_id=store_id,
                date__gte=period2_start,
                date__lte=period2_end
            ).aggregate(
                total=Sum('cash_difference'),
                avg=Avg('cash_difference'),
                count=Count('performance_id')
            )

            p1_total = p1_data['total'] or 0
            p2_total = p2_data['total'] or 0
            change = p1_total - p2_total

            result["comparison"] = {
                "period1": {
                    "total": p1_total,
                    "average": round(p1_data['avg'], 0) if p1_data['avg'] else 0
                },
                "period2": {
                    "total": p2_total,
                    "average": round(p2_data['avg'], 0) if p2_data['avg'] else 0
                },
                "change": {
                    "absolute": change,
                    "direction": "悪化" if abs(p1_total) > abs(p2_total) else "改善" if abs(p1_total) < abs(p2_total) else "変化なし"
                }
            }

        else:
            return json.dumps({
                "status": "error",
                "message": f"未対応のmetric: {metric}. 有効な値: sales, claims, accidents, reports, cash_difference"
            }, ensure_ascii=False)

        return json.dumps(result, ensure_ascii=False, indent=2)

    except Exception as e:
        logger.error(f"Error in compare_periods: {e}", exc_info=True)
        return json.dumps({
            "status": "error",
            "message": f"期間比較エラー: {str(e)}"
        }, ensure_ascii=False)


# ============================================================
# 全店舗統計ツール（All Stores）
# ============================================================

@tool
def get_claim_statistics_all_stores(days: int = 30) -> str:
    """
    全店舗のクレーム統計を取得します。店舗間の比較や全体傾向を把握できます。

    When to use this tool:
    - When user wants to compare claims across all stores (全店舗のクレーム比較)
    - When analyzing overall claim trends (全体的なクレーム傾向)
    - When identifying stores with high/low claim rates

    Args:
        days: 集計期間（日数、デフォルト: 30日）

    Returns:
        全店舗のクレーム統計のJSON文字列
    """
    try:
        from reports.models import DailyReport
        from stores.models import Store
        from django.db.models import Count, Q

        end_date = datetime.now().date()
        start_date = end_date - timedelta(days=days)

        # 全店舗のデータ
        all_reports = DailyReport.objects.filter(
            date__gte=start_date,
            date__lte=end_date
        )

        total_reports = all_reports.count()

        # クレーム
        claim_reports = all_reports.filter(
            genre='claim',
            content__isnull=False
        ).exclude(content='')

        claim_count = claim_reports.count()
        claim_rate = f"{(claim_count / total_reports * 100):.1f}%" if total_reports else "0%"

        # 店舗別クレーム数
        claims_by_store = claim_reports.values(
            'store__store_name'
        ).annotate(
            count=Count('report_id')
        ).order_by('-count')[:10]

        store_breakdown = [
            {"store_name": item['store__store_name'], "count": item['count']}
            for item in claims_by_store
        ]

        # カテゴリ別（location）
        claim_by_location = claim_reports.values('location').annotate(
            count=Count('report_id')
        ).order_by('-count')[:5]

        top_categories = [
            {"category": item['location'], "count": item['count']}
            for item in claim_by_location
        ]

        result = {
            "status": "success",
            "scope": "全店舗",
            "period_days": days,
            "summary": {
                "total_reports": total_reports,
                "claim_count": claim_count,
                "claim_rate": claim_rate
            },
            "store_breakdown": store_breakdown,
            "top_categories": top_categories
        }

        return json.dumps(result, ensure_ascii=False, indent=2)

    except Exception as e:
        logger.error(f"Error in get_claim_statistics_all_stores: {e}", exc_info=True)
        return json.dumps({
            "status": "error",
            "message": f"全店舗クレーム統計取得エラー: {str(e)}"
        }, ensure_ascii=False)


@tool
def get_report_statistics_all_stores(days: int = 30) -> str:
    """
    全店舗の日報統計を取得します。店舗間の活動量や傾向を比較できます。

    When to use this tool:
    - When comparing report submission across stores (店舗間の日報提出状況)
    - When analyzing overall reporting trends (全体的な報告傾向)

    Args:
        days: 集計期間（日数、デフォルト: 30日）

    Returns:
        全店舗の日報統計のJSON文字列
    """
    try:
        from reports.models import DailyReport
        from django.db.models import Count

        end_date = datetime.now().date()
        start_date = end_date - timedelta(days=days)

        # 全店舗の日報
        queryset = DailyReport.objects.filter(
            date__gte=start_date,
            date__lte=end_date
        )

        total_reports = queryset.count()

        if total_reports == 0:
            return json.dumps({
                "status": "no_data",
                "message": f"指定期間（過去{days}日間）の日報データがありません。"
            }, ensure_ascii=False)

        # ジャンル別集計
        genre_breakdown = queryset.values('genre').annotate(
            count=Count('report_id')
        ).order_by('-count')

        genre_data = []
        for item in genre_breakdown:
            genre_display = dict(DailyReport.GENRE_CHOICES).get(item['genre'], item['genre'])
            percentage = (item['count'] / total_reports * 100) if total_reports > 0 else 0
            genre_data.append({
                "genre": item['genre'],
                "genre_display": genre_display,
                "count": item['count'],
                "percentage": f"{percentage:.1f}%"
            })

        # 店舗別集計
        store_breakdown = queryset.values('store__store_name').annotate(
            count=Count('report_id')
        ).order_by('-count')[:10]

        store_data = [
            {"store_name": item['store__store_name'], "count": item['count']}
            for item in store_breakdown
        ]

        result = {
            "status": "success",
            "scope": "全店舗",
            "period_days": days,
            "summary": {
                "total_reports": total_reports,
                "avg_per_day": round(total_reports / days, 1)
            },
            "genre_breakdown": genre_data,
            "store_breakdown": store_data
        }

        return json.dumps(result, ensure_ascii=False, indent=2)

    except Exception as e:
        logger.error(f"Error in get_report_statistics_all_stores: {e}", exc_info=True)
        return json.dumps({
            "status": "error",
            "message": f"全店舗日報統計取得エラー: {str(e)}"
        }, ensure_ascii=False)


@tool
def gather_topic_related_data_all_stores(topic: str, days: int = 30) -> str:
    """
    全店舗から特定トピックに関連するデータを収集します。

    When to use this tool:
    - When analyzing a topic across all stores (全店舗でのトピック分析)
    - When looking for best practices from any store
    - When comprehensive data is needed

    Args:
        topic: トピックキーワード（例: "クレーム", "売上", "接客"）
        days: 検索期間（日数、デフォルト: 30日）

    Returns:
        全店舗のトピック関連データのJSON文字列
    """
    try:
        from reports.models import DailyReport
        from bbs.models import BBSPost, BBSComment
        from django.db.models import Q, Count

        end_date = datetime.now().date()
        start_date = end_date - timedelta(days=days)

        result = {
            "status": "success",
            "topic": topic,
            "scope": "全店舗",
            "period_days": days,
            "data_sources": {}
        }

        # 1. 日報からの情報収集（全店舗）
        daily_reports = DailyReport.objects.filter(
            date__gte=start_date,
            date__lte=end_date
        ).filter(
            Q(title__icontains=topic) | Q(content__icontains=topic)
        ).order_by('-date')[:30]

        reports_data = []
        for report in daily_reports:
            reports_data.append({
                "date": str(report.date),
                "store_name": report.store.store_name if report.store else "不明",
                "genre": dict(DailyReport.GENRE_CHOICES).get(report.genre, report.genre),
                "location": dict(DailyReport.LOCATION_CHOICES).get(report.location, report.location),
                "title": report.title,
                "content": report.content[:300],
                "author": report.user.user_id if report.user else "不明"
            })

        result["data_sources"]["daily_reports"] = {
            "count": len(reports_data),
            "items": reports_data
        }

        # 2. 掲示板からの情報収集（全店舗）
        from django.db.models import Prefetch

        bbs_posts = BBSPost.objects.filter(
            created_at__date__gte=start_date,
            created_at__date__lte=end_date
        ).filter(
            Q(title__icontains=topic) | Q(content__icontains=topic)
        ).prefetch_related(
            Prefetch(
                'comments',
                queryset=BBSComment.objects.select_related('user').order_by('created_at')[:5],
                to_attr='recent_comments'
            ),
            'user',
            'store'
        ).order_by('-created_at')[:20]

        bbs_data = []
        for post in bbs_posts:
            comment_list = [
                {
                    "author": comment.user.user_id if comment.user else "不明",
                    "content": comment.content[:200],
                    "created_at": comment.created_at.strftime("%Y-%m-%d %H:%M")
                }
                for comment in post.recent_comments
            ]

            bbs_data.append({
                "store_name": post.store.store_name if post.store else "不明",
                "title": post.title,
                "content": post.content[:300],
                "author": post.user.user_id if post.user else "不明",
                "created_at": post.created_at.strftime("%Y-%m-%d"),
                "comment_count": post.comment_count,
                "comments": comment_list
            })

        result["data_sources"]["bbs_posts"] = {
            "count": len(bbs_data),
            "items": bbs_data
        }

        # 3. トピックに関連する統計（全店舗）
        topic_lower = topic.lower()
        statistics = {}

        if any(keyword in topic_lower for keyword in ["クレーム", "苦情", "claim"]):
            claim_reports = DailyReport.objects.filter(
                genre='claim',
                date__gte=start_date,
                date__lte=end_date
            )
            statistics["claim_count"] = claim_reports.count()
            statistics["claim_by_store"] = list(
                claim_reports.values('store__store_name')
                .annotate(count=Count('report_id'))
                .order_by('-count')[:5]
            )

        result["data_sources"]["related_statistics"] = statistics

        return json.dumps(result, ensure_ascii=False, indent=2)

    except Exception as e:
        logger.error(f"Error in gather_topic_related_data_all_stores: {e}", exc_info=True)
        return json.dumps({
            "status": "error",
            "message": f"全店舗情報収集エラー: {str(e)}"
        }, ensure_ascii=False)
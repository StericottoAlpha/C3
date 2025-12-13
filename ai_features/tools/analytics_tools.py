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

        # 日別トレンド（最近7日）
        daily_trend = []
        for i in range(min(7, days)):
            target_date = end_date - timedelta(days=i)
            day_claims = claim_reports.filter(date=target_date).count()
            daily_trend.append({
                "date": str(target_date),
                "count": day_claims
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
    売上推移データを取得します。指定期間の売上合計、平均、日別推移などを分析します。

    Args:
        store_id: 店舗ID
        days: 集計日数（デフォルト: 30日）

    Returns:
        売上推移データのJSON文字列
    """
    return json.dumps({
        "status": "not_available",
        "message": "現在のシステムでは売上データは日報に記録されていません。売上に関する情報が必要な場合は、日報の内容を検索してください。"
    }, ensure_ascii=False)


@tool
def get_cash_difference_analysis(store_id: int, days: int = 30) -> str:
    """
    現金過不足分析データを取得します。指定期間の違算金額、発生頻度などを分析します。

    Args:
        store_id: 店舗ID
        days: 集計日数（デフォルト: 30日）

    Returns:
        現金過不足分析のJSON文字列
    """
    return json.dumps({
        "status": "not_available",
        "message": "現在のシステムでは現金過不足データは日報に記録されていません。現金過不足に関する情報が必要な場合は、日報の内容を検索してください。"
    }, ensure_ascii=False)

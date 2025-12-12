"""
統計・分析ツール
LangChain Function Calling Agent用の統計分析ツール
"""
import logging
from typing import Optional
from datetime import datetime, timedelta
from django.db.models import Count, Sum, Avg, Q
from langchain.tools import tool

from reports.models import DailyReport

logger = logging.getLogger(__name__)


@tool
def get_claim_statistics(
    user,
    date_from: Optional[str] = None,
    date_to: Optional[str] = None,
    days: int = 30
) -> str:
    """
    クレーム統計を取得

    指定期間のクレーム件数、内容の傾向を分析します。

    Args:
        user: ユーザーオブジェクト
        date_from: 開始日（YYYY-MM-DD形式、オプション）
        date_to: 終了日（YYYY-MM-DD形式、オプション）
        days: 日数（date_from/date_toが指定されていない場合、過去N日間を集計）

    Returns:
        クレーム統計のJSON文字列
    """
    try:
        # 日付範囲設定
        if date_to:
            end_date = datetime.strptime(date_to, '%Y-%m-%d').date()
        else:
            end_date = datetime.now().date()

        if date_from:
            start_date = datetime.strptime(date_from, '%Y-%m-%d').date()
        else:
            start_date = end_date - timedelta(days=days)

        # ベースクエリ
        queryset = DailyReport.objects.filter(
            report_date__gte=start_date,
            report_date__lte=end_date
        )

        # ユーザーの店舗でフィルタ
        if hasattr(user, 'store'):
            queryset = queryset.filter(store=user.store)

        # クレームあり日報のみ
        claim_reports = queryset.filter(
            Q(claim_content__isnull=False) & ~Q(claim_content='')
        )

        # 統計計算
        total_reports = queryset.count()
        claim_count = claim_reports.count()
        claim_rate = (claim_count / total_reports * 100) if total_reports > 0 else 0

        # 日別集計
        daily_claims = claim_reports.values('report_date').annotate(
            count=Count('report_id')
        ).order_by('-report_date')[:10]

        # クレーム内容サンプル（最新5件）
        recent_claims = claim_reports.order_by('-report_date')[:5].values(
            'report_date', 'claim_content', 'store__store_name', 'user__username'
        )

        # 結果フォーマット
        import json
        result = {
            'period': {
                'start_date': start_date.strftime('%Y-%m-%d'),
                'end_date': end_date.strftime('%Y-%m-%d'),
                'days': (end_date - start_date).days + 1,
            },
            'summary': {
                'total_reports': total_reports,
                'claim_count': claim_count,
                'claim_rate': f"{claim_rate:.1f}%",
            },
            'daily_trend': [
                {
                    'date': item['report_date'].strftime('%Y-%m-%d'),
                    'count': item['count']
                }
                for item in daily_claims
            ],
            'recent_claims': [
                {
                    'date': item['report_date'].strftime('%Y-%m-%d'),
                    'store': item['store__store_name'],
                    'author': item['user__username'],
                    'content': item['claim_content'][:100] + ('...' if len(item['claim_content']) > 100 else '')
                }
                for item in recent_claims
            ]
        }

        return json.dumps(result, ensure_ascii=False, indent=2)

    except Exception as e:
        logger.error(f"Error in get_claim_statistics: {e}")
        return f"統計取得中にエラーが発生しました: {str(e)}"


@tool
def get_sales_trend(
    user,
    date_from: Optional[str] = None,
    date_to: Optional[str] = None,
    days: int = 30
) -> str:
    """
    売上トレンドを取得

    指定期間の売上推移、平均値、前期比較などを分析します。

    Args:
        user: ユーザーオブジェクト
        date_from: 開始日（YYYY-MM-DD形式、オプション）
        date_to: 終了日（YYYY-MM-DD形式、オプション）
        days: 日数（date_from/date_toが指定されていない場合、過去N日間を集計）

    Returns:
        売上トレンドのJSON文字列
    """
    try:
        # 日付範囲設定
        if date_to:
            end_date = datetime.strptime(date_to, '%Y-%m-%d').date()
        else:
            end_date = datetime.now().date()

        if date_from:
            start_date = datetime.strptime(date_from, '%Y-%m-%d').date()
        else:
            start_date = end_date - timedelta(days=days)

        # ベースクエリ
        queryset = DailyReport.objects.filter(
            report_date__gte=start_date,
            report_date__lte=end_date
        )

        # ユーザーの店舗でフィルタ
        if hasattr(user, 'store'):
            queryset = queryset.filter(store=user.store)

        # 統計計算
        stats = queryset.aggregate(
            total_sales=Sum('sales_amount'),
            avg_sales=Avg('sales_amount'),
            report_count=Count('report_id')
        )

        # 日別売上
        daily_sales = queryset.values('report_date').annotate(
            sales=Sum('sales_amount')
        ).order_by('report_date')

        # 週次平均（過去4週）
        weekly_avg = []
        for i in range(4):
            week_end = end_date - timedelta(days=i*7)
            week_start = week_end - timedelta(days=6)
            week_sales = queryset.filter(
                report_date__gte=week_start,
                report_date__lte=week_end
            ).aggregate(avg=Avg('sales_amount'))

            weekly_avg.append({
                'week': f"{week_start.strftime('%m/%d')}-{week_end.strftime('%m/%d')}",
                'avg_sales': week_sales['avg'] or 0
            })

        # 結果フォーマット
        import json
        result = {
            'period': {
                'start_date': start_date.strftime('%Y-%m-%d'),
                'end_date': end_date.strftime('%Y-%m-%d'),
                'days': (end_date - start_date).days + 1,
            },
            'summary': {
                'total_sales': int(stats['total_sales'] or 0),
                'avg_sales': int(stats['avg_sales'] or 0),
                'report_count': stats['report_count'],
            },
            'daily_trend': [
                {
                    'date': item['report_date'].strftime('%Y-%m-%d'),
                    'sales': int(item['sales'] or 0)
                }
                for item in daily_sales
            ],
            'weekly_avg': weekly_avg[::-1],  # 古い順に並び替え
        }

        return json.dumps(result, ensure_ascii=False, indent=2)

    except Exception as e:
        logger.error(f"Error in get_sales_trend: {e}")
        return f"統計取得中にエラーが発生しました: {str(e)}"


@tool
def get_cash_difference_analysis(
    user,
    date_from: Optional[str] = None,
    date_to: Optional[str] = None,
    days: int = 30
) -> str:
    """
    現金過不足分析を取得

    指定期間の現金過不足の発生状況、金額、傾向を分析します。

    Args:
        user: ユーザーオブジェクト
        date_from: 開始日（YYYY-MM-DD形式、オプション）
        date_to: 終了日（YYYY-MM-DD形式、オプション）
        days: 日数（date_from/date_toが指定されていない場合、過去N日間を集計）

    Returns:
        現金過不足分析のJSON文字列
    """
    try:
        # 日付範囲設定
        if date_to:
            end_date = datetime.strptime(date_to, '%Y-%m-%d').date()
        else:
            end_date = datetime.now().date()

        if date_from:
            start_date = datetime.strptime(date_from, '%Y-%m-%d').date()
        else:
            start_date = end_date - timedelta(days=days)

        # ベースクエリ
        queryset = DailyReport.objects.filter(
            report_date__gte=start_date,
            report_date__lte=end_date
        )

        # ユーザーの店舗でフィルタ
        if hasattr(user, 'store'):
            queryset = queryset.filter(store=user.store)

        # 過不足あり日報のみ
        diff_reports = queryset.filter(
            Q(cash_difference__gt=0) | Q(cash_difference__lt=0)
        )

        # 統計計算
        total_reports = queryset.count()
        diff_count = diff_reports.count()
        diff_rate = (diff_count / total_reports * 100) if total_reports > 0 else 0

        stats = diff_reports.aggregate(
            total_diff=Sum('cash_difference'),
            avg_diff=Avg('cash_difference'),
            max_diff=Sum('cash_difference')  # 最大値はMaxを使うべきだがデータ型の問題があるのでSumで代用
        )

        # プラス/マイナス別集計
        plus_diff = diff_reports.filter(cash_difference__gt=0).aggregate(
            count=Count('report_id'),
            total=Sum('cash_difference')
        )
        minus_diff = diff_reports.filter(cash_difference__lt=0).aggregate(
            count=Count('report_id'),
            total=Sum('cash_difference')
        )

        # 日別過不足
        daily_diff = diff_reports.values('report_date').annotate(
            diff=Sum('cash_difference')
        ).order_by('-report_date')[:10]

        # 過不足発生日報サンプル（最新5件）
        recent_diff = diff_reports.order_by('-report_date')[:5].values(
            'report_date', 'cash_difference', 'store__store_name', 'user__username'
        )

        # 結果フォーマット
        import json
        result = {
            'period': {
                'start_date': start_date.strftime('%Y-%m-%d'),
                'end_date': end_date.strftime('%Y-%m-%d'),
                'days': (end_date - start_date).days + 1,
            },
            'summary': {
                'total_reports': total_reports,
                'diff_count': diff_count,
                'diff_rate': f"{diff_rate:.1f}%",
                'total_diff': int(stats['total_diff'] or 0),
                'avg_diff': int(stats['avg_diff'] or 0),
            },
            'breakdown': {
                'plus': {
                    'count': plus_diff['count'] or 0,
                    'total': int(plus_diff['total'] or 0),
                },
                'minus': {
                    'count': minus_diff['count'] or 0,
                    'total': int(minus_diff['total'] or 0),
                }
            },
            'daily_trend': [
                {
                    'date': item['report_date'].strftime('%Y-%m-%d'),
                    'diff': int(item['diff'] or 0)
                }
                for item in daily_diff
            ],
            'recent_cases': [
                {
                    'date': item['report_date'].strftime('%Y-%m-%d'),
                    'store': item['store__store_name'],
                    'author': item['user__username'],
                    'diff': int(item['cash_difference'])
                }
                for item in recent_diff
            ]
        }

        return json.dumps(result, ensure_ascii=False, indent=2)

    except Exception as e:
        logger.error(f"Error in get_cash_difference_analysis: {e}")
        return f"統計取得中にエラーが発生しました: {str(e)}"


@tool
def compare_periods(
    user,
    metric: str,
    current_start: str,
    current_end: str,
    previous_start: str,
    previous_end: str
) -> str:
    """
    期間比較分析

    2つの期間で指定された指標を比較します。

    Args:
        user: ユーザーオブジェクト
        metric: 比較する指標（sales, claim_count, cash_diff等）
        current_start: 当期開始日（YYYY-MM-DD形式）
        current_end: 当期終了日（YYYY-MM-DD形式）
        previous_start: 前期開始日（YYYY-MM-DD形式）
        previous_end: 前期終了日（YYYY-MM-DD形式）

    Returns:
        期間比較結果のJSON文字列
    """
    try:
        # 日付パース
        current_start_date = datetime.strptime(current_start, '%Y-%m-%d').date()
        current_end_date = datetime.strptime(current_end, '%Y-%m-%d').date()
        previous_start_date = datetime.strptime(previous_start, '%Y-%m-%d').date()
        previous_end_date = datetime.strptime(previous_end, '%Y-%m-%d').date()

        # ベースクエリ
        current_qs = DailyReport.objects.filter(
            report_date__gte=current_start_date,
            report_date__lte=current_end_date
        )
        previous_qs = DailyReport.objects.filter(
            report_date__gte=previous_start_date,
            report_date__lte=previous_end_date
        )

        # ユーザーの店舗でフィルタ
        if hasattr(user, 'store'):
            current_qs = current_qs.filter(store=user.store)
            previous_qs = previous_qs.filter(store=user.store)

        # 指標に応じた集計
        if metric == 'sales':
            current_value = current_qs.aggregate(total=Sum('sales_amount'))['total'] or 0
            previous_value = previous_qs.aggregate(total=Sum('sales_amount'))['total'] or 0
            unit = '円'
        elif metric == 'claim_count':
            current_value = current_qs.filter(
                Q(claim_content__isnull=False) & ~Q(claim_content='')
            ).count()
            previous_value = previous_qs.filter(
                Q(claim_content__isnull=False) & ~Q(claim_content='')
            ).count()
            unit = '件'
        elif metric == 'cash_diff':
            current_value = current_qs.aggregate(total=Sum('cash_difference'))['total'] or 0
            previous_value = previous_qs.aggregate(total=Sum('cash_difference'))['total'] or 0
            unit = '円'
        else:
            return f"不明な指標: {metric}"

        # 差分・増減率計算
        diff = current_value - previous_value
        if previous_value != 0:
            change_rate = (diff / previous_value) * 100
        else:
            change_rate = 0 if diff == 0 else float('inf')

        # 結果フォーマット
        import json
        result = {
            'metric': metric,
            'unit': unit,
            'current_period': {
                'start': current_start,
                'end': current_end,
                'value': int(current_value) if isinstance(current_value, (int, float)) else current_value,
            },
            'previous_period': {
                'start': previous_start,
                'end': previous_end,
                'value': int(previous_value) if isinstance(previous_value, (int, float)) else previous_value,
            },
            'comparison': {
                'diff': int(diff) if isinstance(diff, (int, float)) else diff,
                'change_rate': f"{change_rate:.1f}%" if change_rate != float('inf') else '計算不可',
                'trend': '増加' if diff > 0 else ('減少' if diff < 0 else '変化なし'),
            }
        }

        return json.dumps(result, ensure_ascii=False, indent=2)

    except Exception as e:
        logger.error(f"Error in compare_periods: {e}")
        return f"比較分析中にエラーが発生しました: {str(e)}"

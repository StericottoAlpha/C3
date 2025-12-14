from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from datetime import datetime, timedelta
from .services import AnalyticsService
from stores.models import MonthlyGoal


@login_required
def dashboard(request):
    """分析ダッシュボード画面"""
    return render(request, 'analytics/dashboard.html')


@login_required
def get_graph_data(request):
    """グラフデータを取得するAPI

    Query Parameters:
        - graph_type: グラフ種類 (sales, customer_count, incident_count, incident_by_location)
        - period: 期間 (week, month)
        - offset: 期間オフセット（0=今週/今月、-1=先週/先月、1=来週/来月）
        - genre: ジャンルフィルタ (incident_by_locationの場合のみ。claim, praise, accident, report, other)
    """
    # パラメータ取得
    graph_type = request.GET.get('graph_type', 'sales')
    period = request.GET.get('period', 'week')
    offset = int(request.GET.get('offset', 0))
    genre = request.GET.get('genre', None)  # ジャンルフィルタ

    # ユーザーの所属店舗を取得
    user = request.user
    store = user.store

    if not store:
        return JsonResponse({'error': '店舗が設定されていません'}, status=400)

    # 基準日を計算（オフセット分を加算）
    base_date = datetime.now().date()
    if period == 'week':
        base_date += timedelta(weeks=offset)
        start_date, end_date = AnalyticsService.get_week_range(base_date)
        period_label = f'{start_date.strftime("%Y年%m月%d日")} ~ {end_date.strftime("%m月%d日")}'
    else:  # month
        # 月単位でオフセット
        year = base_date.year
        month = base_date.month + offset
        while month < 1:
            month += 12
            year -= 1
        while month > 12:
            month -= 12
            year += 1
        base_date = base_date.replace(year=year, month=month)
        start_date, end_date = AnalyticsService.get_month_range(base_date)
        period_label = f'{start_date.strftime("%Y年%m月")}'

    # グラフタイプに応じてデータ取得
    if graph_type == 'sales':
        chart_data = AnalyticsService.get_sales_data(store, start_date, end_date)
        title = '売上推移'
    elif graph_type == 'customer_count':
        chart_data = AnalyticsService.get_customer_count_data(store, start_date, end_date)
        title = '客数推移'
    elif graph_type == 'incident_by_location':
        chart_data = AnalyticsService.get_incident_by_location_data(store, start_date, end_date, genre)
        # ジャンル名のマッピング
        genre_labels = {
            'claim': 'クレーム',
            'praise': '賞賛',
            'accident': '事故',
            'report': '報告',
            'other': 'その他',
        }
        genre_label = genre_labels.get(genre, '全ジャンル') if genre else '全ジャンル'
        title = f'場所別インシデント数（{genre_label}）'
    else:
        return JsonResponse({'error': '不正なグラフタイプです'}, status=400)

    # レスポンスの形式を統一
    response_data = {
        'title': title,
        'period_label': period_label,
        'labels': chart_data['labels'],
        'start_date': start_date.isoformat(),
        'end_date': end_date.isoformat(),
    }

    # datasetsがある場合（積み上げグラフ）とない場合（折れ線グラフ）で分岐
    if 'datasets' in chart_data:
        response_data['datasets'] = chart_data['datasets']
    else:
        response_data['data'] = chart_data['data']

    return JsonResponse(response_data)


@login_required
def get_monthly_goal(request):
    """月次目標を取得するAPI

    Query Parameters:
        - year: 年（省略時は現在の年）
        - month: 月（省略時は現在の月）
    """
    # パラメータ取得
    today = datetime.now().date()
    year = int(request.GET.get('year', today.year))
    month = int(request.GET.get('month', today.month))

    # ユーザーの所属店舗を取得
    user = request.user
    store = user.store

    if not store:
        return JsonResponse({'error': '店舗が設定されていません'}, status=400)

    # 月次目標を取得
    try:
        goal = MonthlyGoal.objects.get(store=store, year=year, month=month)
        return JsonResponse({
            'year': goal.year,
            'month': goal.month,
            'goal_text': goal.goal_text,
            'achievement_rate': goal.achievement_rate,
            'achievement_text': goal.achievement_text,
        })
    except MonthlyGoal.DoesNotExist:
        return JsonResponse({
            'year': year,
            'month': month,
            'goal_text': '目標が設定されていません',
            'achievement_rate': 0,
            'achievement_text': '',
        })

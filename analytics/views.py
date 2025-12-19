from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.shortcuts import render

from .services import AnalyticsService


@login_required
def dashboard(request, default_scope='own'):
    """分析ダッシュボード画面"""
    return render(request, 'analytics/dashboard.html', {'default_scope': default_scope})


@login_required
def get_graph_data(request):
    """グラフデータを取得するAPI"""
    # リクエストパラメータの取得
    graph_type = request.GET.get('graph_type', 'sales')
    period = request.GET.get('period', 'week')
    offset = int(request.GET.get('offset', 0))
    genre = request.GET.get('genre', None)

    # スコープ（own/all）を取得
    scope = request.GET.get('scope', 'own')
    if scope == 'all':
        store = None
    else:
        # ユーザーの所属店舗を取得
        store = request.user.store
        if not store:
            return JsonResponse({'error': '店舗が設定されていません'}, status=400)

    # 期間の日付範囲とラベルを計算
    start_date, end_date, period_label = AnalyticsService.calculate_period_dates(period, offset)

    # 全店舗のときは場所別インシデントに限り自動的に比較モード（自店舗 vs 他店平均）にする
    base_store = None
    if scope == 'all' and graph_type == 'incident_by_location':
        base_store = request.user.store
        if not base_store:
            return JsonResponse({'error': '店舗が設定されていません'}, status=400)

    # グラフデータを取得
    try:
        result = AnalyticsService.get_graph_data_by_type(
            graph_type, store, start_date, end_date, genre, base_store
        )
    except ValueError as e:
        return JsonResponse({'error': str(e)}, status=400)

    # レスポンスの構築
    chart_data = result['chart_data']
    response_data = {
        'title': result['title'],
        'period_label': period_label,
        'labels': chart_data['labels'],
        'start_date': start_date.isoformat(),
        'end_date': end_date.isoformat(),
    }

    # datasetsがある場合（積み上げグラフ or 複数ライン）とない場合（単一折れ線）で分岐
    if 'datasets' in chart_data:
        response_data['datasets'] = chart_data['datasets']
    else:
        response_data['data'] = chart_data['data']

    # chart_kind があればクライアントに返す（例: 'line'）
    if 'chart_kind' in chart_data:
        response_data['chart_kind'] = chart_data['chart_kind']

    return JsonResponse(response_data)


@login_required
def get_monthly_goal(request):
    """月次目標を取得するAPI"""

    # ユーザーの所属店舗を取得
    store = request.user.store
    if not store:
        return JsonResponse({'error': '店舗が設定されていません'}, status=400)

    # パラメータ取得
    year = request.GET.get('year')
    month = request.GET.get('month')

    # 文字列から整数に変換（Noneの場合はNoneのまま）
    year = int(year) if year else None
    month = int(month) if month else None

    # 月次目標データを取得
    goal_data = AnalyticsService.get_monthly_goal_data(store, year, month)

    return JsonResponse(goal_data)

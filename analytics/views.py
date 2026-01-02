from datetime import date
import calendar as pycal

from django.contrib.auth.decorators import login_required
from django.db.models import Count, Max
from django.shortcuts import render, get_object_or_404
from django.utils import timezone
from django.http import JsonResponse
from django.utils.dateparse import parse_date
from django.urls import reverse
from .services import AnalyticsService

from reports.models import DailyReport, StoreDailyPerformance


def _normalize_genre(raw: str) -> str:
    if not raw:
        return "other"
    g = str(raw).strip().lower()
    mapping = {
        "claim": "claim",
        "praise": "praise",
        "report": "report",
        "accident": "trouble",
        "trouble": "trouble",
    }
    return mapping.get(g, "other")


def _shift_month(year: int, month: int, delta: int):
    m = month + delta
    y = year
    while m <= 0:
        m += 12
        y -= 1
    while m >= 13:
        m -= 12
        y += 1
    return y, m


@login_required
def calendar_view(request):
    today = timezone.localdate()
    store = getattr(request.user, "store", None)

    year_q = request.GET.get("year")
    month_q = request.GET.get("month")

    if year_q and month_q:
        year = int(year_q)
        month = int(month_q)
    else:
        base_date = today
        year = base_date.year
        month = base_date.month

    first = date(year, month, 1)
    last = date(year, month, pycal.monthrange(year, month)[1])

    cal = pycal.Calendar(firstweekday=6)
    weeks = cal.monthdatescalendar(year, month)

    perf_qs = StoreDailyPerformance.objects.filter(date__range=(first, last))
    if store is not None:
        perf_qs = perf_qs.filter(store=store)
    sales_map = {p.date: p.sales_amount for p in perf_qs}

    rep_qs = DailyReport.objects.filter(date__range=(first, last))
    if store is not None:
        rep_qs = rep_qs.filter(store=store)

    raw = rep_qs.values("date", "genre").annotate(cnt=Count("pk"))

    counts_map = {}
    for r in raw:
        d = r["date"]
        g = _normalize_genre(r["genre"])
        counts_map.setdefault(d, {}).setdefault(g, 0)
        counts_map[d][g] += r["cnt"]

    def make_cell(d: date):
        c = counts_map.get(d, {})
        sales = sales_map.get(d)
        return {
            "date": d,
            "in_month": (d.month == month),
            "sales_yen": sales_map.get(d),
            "sales_yen_str": f"{int(sales):,}" if sales is not None else None,
            "claim": c.get("claim", 0),
            "trouble": c.get("trouble", 0),
            "praise": c.get("praise", 0),
            "report": c.get("report", 0),
            "other": c.get("other", 0),
        }

    calendar_grid = [[make_cell(d) for d in week] for week in weeks]

    prev_y, prev_m = _shift_month(year, month, -1)
    next_y, next_m = _shift_month(year, month, +1)

    return render(request, "analytics/calendar.html", {
        "year": year,
        "month": month,
        "month_name": pycal.month_name[month],
        "prev": {"year": prev_y, "month": prev_m},
        "next": {"year": next_y, "month": next_m},
        "calendar_grid": calendar_grid,
    })


# ✅追加：その日の一覧を返す（Bottom Sheet用）
@login_required
def calendar_day_api(request, ymd: str):
    store = getattr(request.user, "store", None)

    d = parse_date(ymd)  # "2025-10-10"
    if d is None:
        return JsonResponse({"ok": False, "error": "invalid date"}, status=400)

    # 売上
    perf_qs = StoreDailyPerformance.objects.filter(date=d)
    if store is not None:
        perf_qs = perf_qs.filter(store=store)
    perf = perf_qs.first()

    # 日報一覧
    qs = DailyReport.objects.filter(date=d)
    if store is not None:
        qs = qs.filter(store=store)
    qs = qs.order_by("created_at")

    items = []
    for r in qs:
        gkey = _normalize_genre(r.genre)
        items.append({
            "id": r.pk,
            "title": getattr(r, "title", "") or "（タイトル未設定）",
            "place": getattr(r, "place", "") or "",
            "genre_key": gkey,
            "time": timezone.localtime(r.created_at).strftime("%H:%M") if r.created_at else "",
            "detail_url": reverse("analytics:calendar_detail", args=[r.pk]),
        })

    return JsonResponse({
        "ok": True,
        "ymd": ymd,
        "date_label": d.strftime("%Y年%m月%d日"),
        "sales_yen": perf.sales_amount if perf else None,
        "items": items,
    })


# ✅追加：日報詳細ページ（カレンダーから飛ぶ先）
@login_required
def calendar_detail(request, report_id: int):
    store = getattr(request.user, "store", None)

    qs = DailyReport.objects.all()
    if store is not None:
        qs = qs.filter(store=store)

    report = get_object_or_404(qs, pk=report_id)

    gkey = _normalize_genre(report.genre)
    label_map = {
        "claim": "クレーム",
        "trouble": "故障",
        "praise": "賞賛",
        "report": "報告",
        "other": "その他",
    }

    return render(request, "analytics/calendar_detail.html", {
        "report": report,
        "genre_key": gkey,
        "genre_label": label_map.get(gkey, "その他"),
        "dt_label": timezone.localtime(report.created_at).strftime("%Y年%m月%d日 %H:%M") if report.created_at else "",
    })


@login_required
def dashboard(request):
    """分析ダッシュボード画面"""
    return render(request, 'analytics/dashboard.html')


@login_required
def get_graph_data(request):
    """グラフデータを取得するAPI"""
    # リクエストパラメータの取得
    graph_type = request.GET.get('graph_type', 'sales')
    period = request.GET.get('period', 'week')
    offset = int(request.GET.get('offset', 0))
    genre = request.GET.get('genre', None)
    location = request.GET.get('location', None)

    # ユーザーの所属店舗を取得
    store = request.user.store
    if not store:
        return JsonResponse({'error': '店舗が設定されていません'}, status=400)

    # 期間の日付範囲とラベルを計算
    start_date, end_date, period_label = AnalyticsService.calculate_period_dates(period, offset)

    # グラフデータを取得
    try:
        result = AnalyticsService.get_graph_data_by_type(
            graph_type, store, start_date, end_date, genre, period=period, location=location
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

    # datasetsがある場合（積み上げグラフ）とない場合（折れ線グラフ）で分岐
    if 'datasets' in chart_data:
        response_data['datasets'] = chart_data['datasets']
    else:
        response_data['data'] = chart_data['data']

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

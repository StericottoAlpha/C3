from datetime import date
import calendar as pycal

from django.contrib.auth.decorators import login_required
from django.db.models import Count, Max
from django.shortcuts import render
from django.utils import timezone

from reports.models import DailyReport, StoreDailyPerformance

def _normalize_genre(raw: str) -> str:
    """
    DailyReport.genre をカレンダー表示用のキーに正規化する。
    template 側が claim/trouble/praise/report/other を参照する想定。
    """
    if not raw:
        return "other"

    g = str(raw).strip().lower()

    mapping = {
        "claim": "claim",
        "praise": "praise",
        "report": "report",

        # seed にある accident をカレンダー側の trouble に寄せる
        "accident": "trouble",

        # もし genre に trouble が直接入ってくる場合もそのまま
        "trouble": "trouble",
    }
    return mapping.get(g, "other")


def _shift_month(year: int, month: int, delta: int):
    """
    (year, month) を delta ヶ月だけ進める/戻す。
    delta = -1 で前月、+1 で翌月。
    """
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

    # 店舗で絞る（ユーザーに store が付いている想定）
    store = getattr(request.user, "store", None)

    # ✅ year/month がURLで指定されていない場合は、
    #    日報の「最終更新(created_at)」の月を初期表示にする
    year_q = request.GET.get("year")
    month_q = request.GET.get("month")

    if year_q and month_q:
        year = int(year_q)
        month = int(month_q)
    else:
        rep_qs0 = DailyReport.objects.all()
        if store is not None:
            rep_qs0 = rep_qs0.filter(store=store)

        latest_dt = rep_qs0.aggregate(m=Max("created_at"))["m"]
        base_date = timezone.localtime(latest_dt).date() if latest_dt else today

        year = base_date.year
        month = base_date.month

    first = date(year, month, 1)
    last = date(year, month, pycal.monthrange(year, month)[1])

    # 日曜始まり（前後月の日付も含む）
    cal = pycal.Calendar(firstweekday=6)
    weeks = cal.monthdatescalendar(year, month)

    # -----------------------------
    # 売上（StoreDailyPerformance）
    # -----------------------------
    perf_qs = StoreDailyPerformance.objects.filter(date__range=(first, last))
    if store is not None:
        perf_qs = perf_qs.filter(store=store)
    sales_map = {p.date: p.sales_amount for p in perf_qs}

    # -----------------------------
    # 日報（DailyReport） genre集計
    # -----------------------------
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
        return {
            "date": d,
            "in_month": (d.month == month),
            "sales_yen": sales_map.get(d),
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



@login_required
def dashboard(request):
    return render(request, 'analytics/dashboard.html')

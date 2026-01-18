from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone
from django.db.models import Q
from itertools import groupby
from operator import attrgetter
import logging
from .forms import DailyReportForm
from .models import DailyReport, ReportImage, StoreDailyPerformance
from bbs.models import BBSPost

logger = logging.getLogger(__name__)


@login_required
def report_register(request):
    """日報登録ビュー"""

    if request.method == 'POST':
        form = DailyReportForm(request.POST, request.FILES)

        if form.is_valid():
            # 日報を保存（まだDBにコミットしない）
            report = form.save(commit=False)
            report.store = request.user.store
            report.user = request.user
            report.date = timezone.now().date()
            report.save()

            # 画像を保存（1枚のみ）
            image = request.FILES.get('image')
            if image:
                try:
                    ReportImage.objects.create(
                        report=report,
                        file_path=image
                    )
                    logger.info(f"Image uploaded successfully for report {report.report_id}")
                except Exception as e:
                    logger.error(f"Image upload failed: {e}", exc_info=True)
                    raise  # 一時的に再スロー（エラー内容を確認するため）

            # 掲示板に投稿する場合
            if report.post_to_bbs:
                BBSPost.objects.create(
                    store=report.store,
                    user=report.user,
                    report=report,
                    title=report.title,
                    content=report.content,
                    comment_count=0
                )

            return redirect('common:index')  # ホーム画面にリダイレクト
        else:
            messages.error(request, '入力内容に誤りがあります。')
    else:
        form = DailyReportForm()

    context = {
        'form': form,
    }
    return render(request, 'reports/register.html', context)



@login_required
def report_view(request, report_id):
    """View a single daily report"""

    # Get report with related data
    report = get_object_or_404(
        DailyReport.objects.select_related('store', 'user').prefetch_related('images'),
        report_id=report_id
    )

    context = {
        'report': report,
    }

    return render(request, 'reports/view.html', context)


@login_required
def report_list(request):
    """日報一覧ビュー"""
    from django.core.paginator import Paginator

    reports = DailyReport.objects.select_related('user', 'store').filter(store=request.user.store)

    # ジャンルでフィルタリング
    genre = request.GET.get('genre')
    if genre:
        reports = reports.filter(genre=genre)

    # 場所でフィルタリング
    location = request.GET.get('location')
    if location:
        reports = reports.filter(location=location)

    # キーワード検索
    query = request.GET.get('query')
    if query:
        keywords = query.replace('　', ' ').split()
        if keywords:
            query_condition = Q()
            for word in keywords:
                query_condition |= Q(title__icontains=word) | Q(content__icontains=word)
            reports = reports.filter(query_condition)

    # ソート
    sort_option = request.GET.get('sort')
    if sort_option == 'oldest':
        reports = reports.order_by('date', 'created_at')
    else:
        reports = reports.order_by('-date', '-created_at')

    # 日別表示用：ユニークな日付リストを取得
    if sort_option == 'oldest':
        unique_dates = list(reports.values_list('date', flat=True).distinct().order_by('date'))
    else:
        unique_dates = list(reports.values_list('date', flat=True).distinct().order_by('-date'))

    # 日付リストをページネーション（1ページあたり7日分）
    DAYS_PER_PAGE = 7
    date_paginator = Paginator(unique_dates, DAYS_PER_PAGE)
    page_number = request.GET.get('page', 1)
    date_page = date_paginator.get_page(page_number)

    # 現在のページの日付に対応する日報を取得
    reports_by_date = []
    for date in date_page:
        day_reports = [r for r in reports if r.date == date]

        # その日の売上データを取得
        performance = StoreDailyPerformance.objects.filter(
            store=request.user.store,
            date=date
        ).first()

        reports_by_date.append({
            'date': date,
            'reports': day_reports,
            'count': len(day_reports),
            'performance': performance
        })

    # 検索表示用のページネーション（1ページあたり10件）
    REPORTS_PER_PAGE = 10
    report_paginator = Paginator(reports, REPORTS_PER_PAGE)
    search_page_number = request.GET.get('search_page', 1)
    reports_paginated = report_paginator.get_page(search_page_number)

    # ページネーション用のクエリ文字列を構築（pageパラメータを除く）
    query_params = request.GET.copy()
    if 'page' in query_params:
        del query_params['page']
    if 'search_page' in query_params:
        del query_params['search_page']
    query_string = query_params.urlencode()

    context = {
        'reports': reports_paginated,  # 検索表示用（ページネーション済み）
        'reports_by_date': reports_by_date,
        'date_page': date_page,  # 日別表示用ページネーション
        'query': query,
        'sort': sort_option,
        'genre_choices': DailyReport.GENRE_CHOICES,
        'location_choices': DailyReport.LOCATION_CHOICES,
        'current_genre': genre,
        'current_location': location,
        'query_string': query_string,
    }
    return render(request, 'reports/list.html', context)

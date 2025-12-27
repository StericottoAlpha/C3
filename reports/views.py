from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone
from django.db.models import Q
from itertools import groupby
from operator import attrgetter
from .forms import DailyReportForm
from .models import DailyReport, ReportImage, StoreDailyPerformance
from bbs.models import BBSPost


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
                ReportImage.objects.create(
                    report=report,
                    file_path=image
                )

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

    # 日別グループ化（タブ表示用）
    reports_by_date = []
    for date, group in groupby(reports, key=attrgetter('date')):
        reports_list = list(group)

        # その日の売上データを取得
        performance = StoreDailyPerformance.objects.filter(
            store=request.user.store,
            date=date
        ).first()

        reports_by_date.append({
            'date': date,
            'reports': reports_list,
            'count': len(reports_list),
            'performance': performance
        })

    context = {
        'reports': reports,
        'reports_by_date': reports_by_date,
        'query': query,
        'sort': sort_option,
        'genre_choices': DailyReport.GENRE_CHOICES,
        'location_choices': DailyReport.LOCATION_CHOICES,
        'current_genre': genre,
        'current_location': location,
    }
    return render(request, 'reports/list.html', context)

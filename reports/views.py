from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone
from .forms import DailyReportForm
from .models import DailyReport, ReportImage
from bbs.models import BBSPost
from .models import DailyReport


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

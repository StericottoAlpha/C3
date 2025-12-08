from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required
from .models import DailyReport


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

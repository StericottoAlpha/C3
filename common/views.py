import datetime
from pathlib import Path
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse, FileResponse
# ▼ モデルをインポート
from stores.models import MonthlyGoal

@login_required
def index(request):
    """ホーム画面を表示する"""
    context = {}

    # ▼▼▼ 追加: 所属店舗の今月の目標を取得 ▼▼▼
    if getattr(request.user, 'store', None):
        today = datetime.date.today()
        current_goal = MonthlyGoal.objects.filter(
            store=request.user.store,
            year=today.year,
            month=today.month
        ).first()
        
        context['monthly_goal'] = current_goal
    # ▲▲▲ ここまで ▲▲▲

    return render(request, 'common/index.html', context)

def health(request):
    return HttpResponse(status=200)


def manifest(request):
    """PWA manifest.jsonを配信"""
    file_path = Path(__file__).parent / 'static' / 'common' / 'manifest.json'
    return FileResponse(open(file_path, 'rb'), content_type='application/manifest+json')


def service_worker(request):
    """PWA Service Workerを配信"""
    file_path = Path(__file__).parent / 'static' / 'common' / 'service-worker.js'
    return FileResponse(open(file_path, 'rb'), content_type='application/javascript')
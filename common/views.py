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


@login_required
def debug_storage(request):
    """ストレージ設定デバッグ用（管理者のみ）"""
    from django.http import JsonResponse
    from django.conf import settings
    import os

    if not request.user.is_superuser:
        return JsonResponse({'error': 'Admin only'}, status=403)

    # 環境変数の確認（値は隠す）
    env_vars = {
        'SUPABASE_PROJECT_ID': bool(os.getenv('SUPABASE_PROJECT_ID')),
        'SUPABASE_STORAGE_ACCESS_KEY': bool(os.getenv('SUPABASE_STORAGE_ACCESS_KEY')),
        'SUPABASE_STORAGE_SECRET_KEY': bool(os.getenv('SUPABASE_STORAGE_SECRET_KEY')),
        'SUPABASE_STORAGE_BUCKET': os.getenv('SUPABASE_STORAGE_BUCKET', 'media'),
    }

    # Django設定の確認
    storage_config = {
        'STORAGES_default': getattr(settings, 'STORAGES', {}).get('default', {}),
        'AWS_S3_ENDPOINT_URL': getattr(settings, 'AWS_S3_ENDPOINT_URL', 'NOT SET'),
        'AWS_STORAGE_BUCKET_NAME': getattr(settings, 'AWS_STORAGE_BUCKET_NAME', 'NOT SET'),
        'MEDIA_URL': settings.MEDIA_URL,
    }

    # 実際のストレージバックエンドを確認
    from django.core.files.storage import default_storage
    storage_backend = str(type(default_storage).__name__)

    return JsonResponse({
        'env_vars': env_vars,
        'storage_config': storage_config,
        'storage_backend': storage_backend,
    }, json_dumps_params={'indent': 2})


def manifest(request):
    """PWA manifest.jsonを配信"""
    file_path = Path(__file__).parent / 'static' / 'common' / 'manifest.json'
    return FileResponse(open(file_path, 'rb'), content_type='application/manifest+json')


def service_worker(request):
    """PWA Service Workerを配信"""
    file_path = Path(__file__).parent / 'static' / 'common' / 'service-worker.js'
    return FileResponse(open(file_path, 'rb'), content_type='application/javascript')
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, get_user_model
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_http_methods
from django.http import Http404

from .forms import LoginForm
from . import services  # ビジネスロジック層をインポート

# ユーザーモデルを取得
User = get_user_model()


@require_http_methods(["GET", "POST"])
def login_view(request):
    """ログイン画面"""
    if request.user.is_authenticated:
        return redirect('common:index')

    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            return redirect('common:index')
    else:
        form = LoginForm()

    return render(request, 'accounts/login.html', {'form': form})

@login_required
def profile_view(request):
    """ログインユーザーのプロフィール情報を取得して表示する """
    try:
        # ビジネスロジックは services.py に委譲
        context = services.get_profile_context(request.user.pk)
        return render(request, 'accounts/profile.html', context)

    except Exception as e:
        # デバッグ用にコンソール出力（本番運用時はロガー推奨）
        print(f"Profile Error: {e}")
        raise Http404("ユーザー情報の取得に失敗しました")
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout, get_user_model
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_http_methods
from django.http import Http404

from .forms import LoginForm
from django.contrib.auth.decorators import login_required

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

def logout_view(request):
    """ユーザをログアウトさせる。"""
    logout(request)
    return redirect('accounts:login')
    
@login_required
def profile_view(request):
    """ログインユーザーのプロフィール情報を取得して表示する """
    try:
        # 1. ユーザー情報の取得（N+1対策でstoreも一緒に取得）
        user = get_object_or_404(User.objects.select_related('store'), pk=request.user.pk)

        # 2. 氏名の結合
        full_name = f"{user.last_name} {user.first_name}".strip()
        # もし名前が空ならユーザーIDを表示
        if not full_name:
            full_name = str(user.user_id)

        # 3. 権限（役割）の取得
        role = user.get_user_type_display()

        # 4. 所属店舗名の取得
        store_name = "所属なし"
        if user.store:
            store_name = getattr(user.store, 'store_name', str(user.store))

        context = {
            'full_name': full_name,
            'user_id': user.user_id,
            'role': role,
            'store_name': store_name,
        }

        return render(request, 'accounts/profile.html', context)

    except Exception as e:
        # デバッグ用にコンソール出力（本番運用時はロガー推奨）
        print(f"Profile Error: {e}")
        raise Http404("ユーザー情報の取得に失敗しました")
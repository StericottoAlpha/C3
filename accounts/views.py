from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout, get_user_model
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_http_methods
from django.http import Http404
from django.contrib import messages

from django.core.exceptions import PermissionDenied
from django.contrib import messages
from .forms import LoginForm ,SignupForm, StaffEditForm
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

       
@login_required
@require_http_methods(["GET", "POST"])
def signup_view(request):
    "  管理者によるユーザー追加機能"
    if request.user.user_type not in ['admin','manager'] and not request.user.is_superuser:
        raise PermissionDenied("このページにアクセスする権限がありません。")

    if request.method == 'POST':
        form = SignupForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, f"ユーザー {form.cleaned_data['user_id']} を登録しました。")
            return redirect('accounts:signup')
    else:
        form = SignupForm()

    return render(request, 'accounts/signup.html', {'form': form})
    

@login_required
def staff_list_view(request):
    """スタッフ一覧画面（管理者・店長用）"""
    # 権限チェック：管理者か店長以外ならホームに戻す
    if request.user.user_type not in ['manager', 'admin']:
        return redirect('common:index')

    # 全ユーザーを取得（店舗ごと、ID順に並べる）
    users = User.objects.select_related('store').all().order_by('store', 'user_type', 'user_id')
    
    return render(request, 'accounts/staff_list.html', {'users': users})


@login_required
def staff_edit_view(request, user_id):
    """スタッフ情報の編集画面（管理者・店長用）"""
    # 権限チェック
    if request.user.user_type not in ['manager', 'admin']:
        return redirect('common:index')

    # 編集対象のユーザーを取得（見つからなければ404エラー）
    target_user = get_object_or_404(User, user_id=user_id)

    if request.method == 'POST':
        form = StaffEditForm(request.POST, instance=target_user)
        if form.is_valid():
            form.save()
            messages.success(request, f"{target_user.user_id} の編集を保存しました。")
            return redirect('accounts:staff_list')
    else:
        form = StaffEditForm(instance=target_user)

    context = {
        'form': form,
        'target_user': target_user,
    }
    return render(request, 'accounts/staff_edit.html', context)

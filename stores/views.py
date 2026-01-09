import datetime
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.exceptions import PermissionDenied
from .models import MonthlyGoal
from .forms import MonthlyGoalForm

@login_required
def update_current_month_goal(request):
    """今月の店舗目標を設定・更新するビュー"""
    
    # ▼▼▼ 重要な変更点：店長(manager)以外はアクセス拒否（adminも拒否） ▼▼▼
    if request.user.user_type != 'manager':
        raise PermissionDenied("店長のみが目標を設定できます。")
    
    # 所属店舗チェック
    if not request.user.store:
        messages.error(request, "店舗に所属していないため設定できません。")
        return redirect('common:index')

    store = request.user.store
    today = datetime.date.today()
    
    # 今月の目標データを取得、なければ作成
    goal_obj, created = MonthlyGoal.objects.get_or_create(
        store=store,
        year=today.year,
        month=today.month,
        defaults={'goal_text': ''}
    )

    if request.method == 'POST':
        form = MonthlyGoalForm(request.POST, instance=goal_obj)
        if form.is_valid():
            form.save()
            messages.success(request, f"{today.year}年{today.month}月の店舗目標を更新しました。")
            # 保存後はホームへ
            return redirect('common:index')
    else:
        form = MonthlyGoalForm(instance=goal_obj)

    return render(request, 'stores/update_goal.html', {
        'form': form,
        'year': today.year,
        'month': today.month,
        'store': store
    })
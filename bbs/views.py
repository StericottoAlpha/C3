from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import BBSPost
from .forms import BBSPostForm


@login_required
def bbs_register(request):
    """掲示板投稿登録ビュー"""
    if request.method == 'POST':
        form = BBSPostForm(request.POST, user=request.user)
        if form.is_valid():
            bbs_post = form.save(commit=False)
            bbs_post.user = request.user
            bbs_post.store = request.user.store
            bbs_post.save()
            messages.success(request, '掲示板に投稿しました。')
            return redirect('bbs:list')
        else:
            messages.error(request, '入力内容にエラーがあります。')
    else:
        form = BBSPostForm(user=request.user)
    
    return render(request, 'bbs/register.html', {'form': form})


@login_required
def bbs_list(request):
    """掲示板一覧ビュー"""
    posts = BBSPost.objects.select_related('user', 'store').all()
    return render(request, 'bbs/list.html', {'posts': posts})

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import BBSPost, BBSComment
from .forms import BBSPostForm, BBSCommentForm
from django.db.models import Q


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
    """掲示板一覧ビュー（検索・ソート機能付き）"""
    posts = BBSPost.objects.select_related('user', 'store')

    query = request.GET.get('query')
    if query:
        posts = posts.filter(
            Q(title__icontains=query) | Q(content__icontains=query)
        )

    sort_option = request.GET.get('sort')
    if sort_option == 'oldest':
        posts = posts.order_by('created_at')
    else:
        posts = posts.order_by('-created_at')
    context = {
        'posts': posts,
        'query': query,
        'sort': sort_option,
    }
    return render(request, 'bbs/list.html', context)


@login_required
def bbs_detail(request, bbs_id):
    """掲示板詳細ビュー（モックコメント付き）"""
    post = get_object_or_404(BBSPost.objects.select_related('user', 'store'), post_id=bbs_id)

    all_comments = BBSComment.objects.select_related('user').filter(post=post)

    # ベストアンサーを先頭に、その他を時系列順にソート
    # Pythonでは False < True なので、False（ベストアンサー）が先に来る

    comments = sorted(all_comments, key=lambda x: (not x.is_best_answer, x.created_at))

    context = {
        'post': post,
        'comments': comments,
        'comment_form': BBSCommentForm(),
    }

    return render(request, 'bbs/detail.html', context)


@login_required
def bbs_comment(request, bbs_id):
    if request.method == 'POST':
        form = BBSCommentForm(request.POST)
        if form.is_valid():
            bbs_post = get_object_or_404(BBSPost, post_id=bbs_id)
            bbs_comment = form.save(commit=False)
            bbs_comment.user = request.user
            bbs_comment.post = bbs_post
            bbs_comment.save()
            messages.success(request, 'コメントを投稿しました。')
        else:
            messages.error(request, 'コメントの投稿に失敗しました。')

    return redirect('bbs:detail', bbs_id=bbs_id)

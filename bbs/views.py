from django.shortcuts import render, redirect, get_object_or_404
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


@login_required
def bbs_detail(request, bbs_id):
    """掲示板詳細ビュー（モックコメント付き）"""
    post = get_object_or_404(BBSPost.objects.select_related('user', 'store'), post_id=bbs_id)

    # モックコメントデータ
    all_comments = [
        {
            'user': '佐藤 太郎',
            'content': 'とても参考になる情報ありがとうございます。うちの店舗でも同じような問題がありました。',
            'created_at': '2025/10/10 14:25',
            'is_best_answer': False,
        },
        {
            'user': '田中 花子',
            'content': 'この問題は本部に確認した方が良いと思います。マニュアルにも記載されているはずです。',
            'created_at': '2025/10/10 15:30',
            'is_best_answer': True,
        },
        {
            'user': '鈴木 一郎',
            'content': '私も同じ経験があります。その場合は、まずお客様に丁寧に説明することが大切だと思います。',
            'created_at': '2025/10/10 16:45',
            'is_best_answer': False,
        },
    ]

    # ベストアンサーを先頭に、その他を時系列順にソート
    # Pythonでは False < True なので、False（ベストアンサー）が先に来る
    
    mock_comments = sorted(all_comments, key=lambda x: (not x['is_best_answer'], x['created_at']))

    context = {
        'post': post,
        'comments': mock_comments,
    }

    return render(request, 'bbs/detail.html', context)

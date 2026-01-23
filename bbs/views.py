from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.views.decorators.http import require_POST
import json
from .models import BBSPost, BBSComment, BBSReaction, BBSCommentReaction
from .forms import BBSPostForm, BBSCommentForm
from django.db.models import Q, Count, Exists, OuterRef
from django.core.paginator import Paginator
from stores.models import Store

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
            return redirect('bbs:list')
        else:
            pass
    else:
        form = BBSPostForm(user=request.user)

    return render(request, 'bbs/register.html', {'form': form})


@login_required
def bbs_list(request):
    """掲示板一覧ビュー"""
    NUM_BB_PER_PAGE = 10

    # ✅ 修正1: total_reactions（いいね＋なるほどの合計）を計算に追加
    posts = BBSPost.objects.select_related('user', 'store').annotate(
        naruhodo_count=Count('reactions', filter=Q(reactions__reaction_type='naruhodo')),
        iine_count=Count('reactions', filter=Q(reactions__reaction_type='iine')),
        total_reactions=Count('reactions'),  # 並び替え用に全リアクション数をカウント
        is_naruhodo=Exists(
            BBSReaction.objects.filter(
                post=OuterRef('pk'),
                user=request.user,
                reaction_type='naruhodo'
            )
        ),
        is_iine=Exists(
            BBSReaction.objects.filter(
                post=OuterRef('pk'),
                user=request.user,
                reaction_type='iine'
            )
        ),
    )

    genre = request.GET.get('genre')
    if genre:
        posts = posts.filter(genre=genre)

    store_id = request.GET.get('store')
    if store_id:
        posts = posts.filter(store_id=store_id)

    query = request.GET.get('query')
    if query:
        keywords = query.replace('　', ' ').split()
        if keywords:
            query_condition = Q()
            for word in keywords:
                query_condition |= Q(title__icontains=word) | Q(content__icontains=word)
            posts = posts.filter(query_condition)

    # ✅ 修正2: 'popular' (人気順) のソートロジックを追加
    sort_option = request.GET.get('sort')
    if sort_option == 'oldest':
        posts = posts.order_by('created_at')
    elif sort_option == 'popular':
        # 合計リアクション数の降順、同数の場合は新しい順
        posts = posts.order_by('-total_reactions', '-created_at')
    else:
        posts = posts.order_by('-created_at')

    paginator = Paginator(posts, NUM_BB_PER_PAGE)

    page_number = request.GET.get("page")
    posts_pagenated = paginator.get_page(page_number)

    # ページネーション用のクエリ文字列を構築（pageパラメータを除く）
    query_params = request.GET.copy()
    if 'page' in query_params:
        del query_params['page']
    query_string = query_params.urlencode()

    stores = Store.objects.all().order_by('store_name')

    context = {
        'posts': posts_pagenated,
        'query': query,
        'sort': sort_option,
        'genre_choices': BBSPost.GENRE_CHOICES,
        'current_genre': genre,
        'stores': stores,
        'current_store': store_id,
        'query_string': query_string,
    }
    return render(request, 'bbs/list.html', context)


@login_required
def bbs_detail(request, bbs_id):
    """掲示板詳細ビュー（モックコメント付き）"""
    post = get_object_or_404(BBSPost.objects.select_related('user', 'store').prefetch_related('reactions'), post_id=bbs_id)

    all_comments = BBSComment.objects.select_related('user').prefetch_related('reactions').filter(post=post)

    # ベストアンサーを先頭に、その他を時系列順にソート
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
            # コメント数を更新
            bbs_post.comment_count = bbs_post.comments.count()
            bbs_post.save(update_fields=['comment_count'])
        else:
            pass

    return redirect('bbs:detail', bbs_id=bbs_id)

@login_required
@require_POST
def toggle_reaction(request):
    """
    投稿・コメント共通のリアクション切り替えAPI
    JSONデータ例: { "target_type": "post", "target_id": 1, "reaction_type": "naruhodo" }
    """
    try:
        data = json.loads(request.body)
        target_type = data.get('target_type')  # 'post' or 'comment'
        target_id = data.get('target_id')
        reaction_type = data.get('reaction_type')

        # 1. 対象のモデルとリアクションモデルを切り替える
        if target_type == 'post':
            ModelClass = BBSPost
            ReactionClass = BBSReaction
            id_field = 'post_id'
            related_name = 'reactions'
            lookup_kwargs = {'post_id': target_id} # 検索条件
            reaction_lookup = {'post': None}       # リアクション作成時の紐付けキー
        elif target_type == 'comment':
            ModelClass = BBSComment
            ReactionClass = BBSCommentReaction
            id_field = 'comment_id'
            related_name = 'reactions'
            lookup_kwargs = {'comment_id': target_id}
            reaction_lookup = {'comment': None}
        else:
            return JsonResponse({'error': 'Invalid target type'}, status=400)

        # 2. リアクション種別のバリデーション
        valid_reactions = [choice[0] for choice in ReactionClass.REACTION_CHOICES]
        if reaction_type not in valid_reactions:
            return JsonResponse({'error': 'Invalid reaction type'}, status=400)

        # 3. 対象オブジェクトの取得
        target_obj = get_object_or_404(ModelClass, **lookup_kwargs)

        # 4. リアクションの検索・作成・削除
        # 検索条件の構築 (例: post=target_obj, user=user, reaction_type=...)
        filter_kwargs = reaction_lookup.copy()
        key_name = list(filter_kwargs.keys())[0] # 'post' または 'comment'
        filter_kwargs[key_name] = target_obj
        filter_kwargs['user'] = request.user
        filter_kwargs['reaction_type'] = reaction_type

        reaction = ReactionClass.objects.filter(**filter_kwargs).first()

        if reaction:
            reaction.delete()
            action = 'removed'
        else:
            ReactionClass.objects.create(**filter_kwargs)
            action = 'added'

        # 5. 現在の件数を再取得
        # target_obj.reactions.filter(...)
        count = getattr(target_obj, related_name).filter(reaction_type=reaction_type).count()

        return JsonResponse({
            'status': 'success',
            'action': action,
            'count': count,
            'target_id': target_id,
            'target_type': target_type,
            'reaction_type': reaction_type
        })

    except json.JSONDecodeError:
        return JsonResponse({'error': 'Invalid JSON'}, status=400)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)
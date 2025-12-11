from django.shortcuts import get_object_or_404
from django.contrib.auth import get_user_model

# モデルを取得
User = get_user_model()

def get_profile_context(user_pk) -> dict:
    """
    ユーザーIDからプロフィール画面に必要な情報を取得・加工する
    """
    # 1. ユーザー情報の取得（storeも一緒に取得）
    user = get_object_or_404(User.objects.select_related('store'), pk=user_pk)

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
        # store_name がなければ str(user.store) を使う
        store_name = getattr(user.store, 'store_name', str(user.store))

    # Viewに渡すデータ
    return {
        'full_name': full_name,
        'user_id': user.user_id,  # ここを修正: user.username を削除
        'role': role,
        'store_name': store_name,
    }
from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.utils import timezone


class UserManager(BaseUserManager):
    """カスタムユーザーマネージャー"""

    def create_user(self, user_id, password=None, **extra_fields):
        """通常のユーザーを作成"""
        if not user_id:
            raise ValueError('ユーザーIDは必須です')
        if 'store' not in extra_fields or extra_fields['store'] is None:
            raise ValueError('店舗の指定は必須です')

        user = self.model(user_id=user_id, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, user_id, password=None, **extra_fields):
        """スーパーユーザーを作成"""
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('user_type', 'admin')

        # スーパーユーザー作成時は店舗が未指定の場合、本部店舗を設定
        if 'store' not in extra_fields or extra_fields['store'] is None:
            from stores.models import Store
            # デフォルトの本部店舗を取得または作成
            store, created = Store.objects.get_or_create(
                store_name='本部',
                defaults={'address': '本部所在地', 'sales_target': ''}
            )
            extra_fields['store'] = store

        return self.create_user(user_id, password, **extra_fields)


class User(AbstractBaseUser, PermissionsMixin):
    """ユーザーモデル"""

    USER_TYPE_CHOICES = [
        ('staff', 'スタッフ'),
        ('manager', '店長'),
        ('admin', '管理者'),
    ]

    user_id = models.CharField(
        max_length=20,
        primary_key=True,
        unique=True,
        verbose_name='ユーザーID'
    )
    store = models.ForeignKey(
        'stores.Store',
        on_delete=models.PROTECT,  # 店舗削除時はユーザーを保護
        related_name='users',
        verbose_name='店舗ID'
    )
    user_type = models.CharField(
        max_length=20,
        choices=USER_TYPE_CHOICES,
        default='staff',
        verbose_name='ユーザー種別'
    )
    email = models.EmailField(
        null=True,
        blank=True,
        unique=True,
        verbose_name='メールアドレス'
    )
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='作成日時')
    login_at = models.DateTimeField(null=True, blank=True, verbose_name='ログイン時刻')
    last_access_at = models.DateTimeField(null=True, blank=True, verbose_name='最終アクセス時刻')
    is_active = models.BooleanField(default=True, verbose_name='アカウント有効フラグ')

    # Django管理画面用
    is_staff = models.BooleanField(default=False, verbose_name='スタッフ権限')

    objects = UserManager()

    USERNAME_FIELD = 'user_id'
    REQUIRED_FIELDS = []  # createsuperuser時に追加で入力を求めるフィールド

    class Meta:
        db_table = 'users'
        verbose_name = 'ユーザー'
        verbose_name_plural = 'ユーザー'

    def __str__(self):
        return f"{self.user_id} ({self.get_user_type_display()})"

    def update_last_access(self):
        """最終アクセス時刻を更新"""
        self.last_access_at = timezone.now()
        self.save(update_fields=['last_access_at'])

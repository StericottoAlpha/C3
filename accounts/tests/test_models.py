from django.test import TestCase
from django.contrib.auth import get_user_model
from django.utils import timezone
from stores.models import Store

User = get_user_model()


class UserManagerTest(TestCase):
    """UserManagerのテスト"""

    def setUp(self):
        """テストデータの準備"""
        self.store = Store.objects.create(
            store_name='テスト店舗',
            address='テスト住所'
        )

    def test_create_user_success(self):
        """通常ユーザーが正常に作成できる"""
        user = User.objects.create_user(
            user_id='test001',
            password='testpass123',
            store=self.store
        )
        self.assertEqual(user.user_id, 'test001')
        self.assertTrue(user.check_password('testpass123'))

    def test_create_user_without_user_id_raises_error(self):
        """user_idなしでユーザー作成時にエラーが発生する"""
        with self.assertRaises(ValueError) as context:
            User.objects.create_user(
                user_id='',
                password='testpass123',
                store=self.store
            )
        self.assertEqual(str(context.exception), 'ユーザーIDは必須です')

    def test_create_user_without_store_raises_error(self):
        """店舗指定なしでユーザー作成時にエラーが発生する"""
        with self.assertRaises(ValueError) as context:
            User.objects.create_user(
                user_id='test001',
                password='testpass123'
            )
        self.assertEqual(str(context.exception), '店舗の指定は必須です')

    def test_create_superuser_success(self):
        """スーパーユーザーが正常に作成できる"""
        user = User.objects.create_superuser(
            user_id='admin001',
            password='adminpass123'
        )
        self.assertTrue(user.is_staff)
        self.assertTrue(user.is_superuser)
        self.assertEqual(user.user_type, 'admin')

    def test_create_superuser_creates_default_store(self):
        """スーパーユーザー作成時に本部店舗が自動作成される"""
        user = User.objects.create_superuser(
            user_id='admin001',
            password='adminpass123'
        )
        self.assertIsNotNone(user.store)
        self.assertEqual(user.store.store_name, '本部')


class UserModelTest(TestCase):
    """Userモデルのテスト"""

    def setUp(self):
        """テストデータの準備"""
        self.store = Store.objects.create(
            store_name='テスト店舗',
            address='テスト住所'
        )

    def test_user_creation_with_required_fields(self):
        """必須フィールドでユーザーが作成できる"""
        user = User.objects.create_user(
            user_id='test001',
            password='testpass123',
            store=self.store
        )
        self.assertIsNotNone(user)
        self.assertEqual(user.user_id, 'test001')

    def test_user_default_user_type_is_staff(self):
        """デフォルトのuser_typeがstaffである"""
        user = User.objects.create_user(
            user_id='test001',
            password='testpass123',
            store=self.store
        )
        self.assertEqual(user.user_type, 'staff')

    def test_user_default_is_active_is_true(self):
        """デフォルトのis_activeがTrueである"""
        user = User.objects.create_user(
            user_id='test001',
            password='testpass123',
            store=self.store
        )
        self.assertTrue(user.is_active)

    def test_user_default_is_staff_is_false(self):
        """デフォルトのis_staffがFalseである"""
        user = User.objects.create_user(
            user_id='test001',
            password='testpass123',
            store=self.store
        )
        self.assertFalse(user.is_staff)

    def test_user_default_first_name_is_empty_string(self):
        """デフォルトのfirst_nameが空文字列である"""
        user = User.objects.create_user(
            user_id='test001',
            password='testpass123',
            store=self.store
        )
        self.assertEqual(user.first_name, '')

    def test_user_default_last_name_is_empty_string(self):
        """デフォルトのlast_nameが空文字列である"""
        user = User.objects.create_user(
            user_id='test001',
            password='testpass123',
            store=self.store
        )
        self.assertEqual(user.last_name, '')

    def test_user_str_method(self):
        """__str__メソッドが正しく動作する"""
        user = User.objects.create_user(
            user_id='test001',
            password='testpass123',
            store=self.store,
            user_type='manager'
        )
        self.assertEqual(str(user), 'test001 (店長)')

    def test_user_with_email(self):
        """メールアドレス付きでユーザーが作成できる"""
        user = User.objects.create_user(
            user_id='test001',
            password='testpass123',
            store=self.store,
            email='test@example.com'
        )
        self.assertEqual(user.email, 'test@example.com')

    def test_user_with_names(self):
        """姓名付きでユーザーが作成できる"""
        user = User.objects.create_user(
            user_id='test001',
            password='testpass123',
            store=self.store,
            first_name='太郎',
            last_name='山田'
        )
        self.assertEqual(user.first_name, '太郎')
        self.assertEqual(user.last_name, '山田')

    def test_update_last_access_method(self):
        """update_last_accessメソッドが正しく動作する"""
        user = User.objects.create_user(
            user_id='test001',
            password='testpass123',
            store=self.store
        )
        self.assertIsNone(user.last_access_at)
        
        user.update_last_access()
        user.refresh_from_db()
        
        self.assertIsNotNone(user.last_access_at)
        self.assertIsInstance(user.last_access_at, timezone.datetime)

    def test_created_at_is_set_automatically(self):
        """created_atが自動的に設定される"""
        user = User.objects.create_user(
            user_id='test001',
            password='testpass123',
            store=self.store
        )
        self.assertIsNotNone(user.created_at)
        self.assertIsInstance(user.created_at, timezone.datetime)

    def test_user_email_uniqueness(self):
        """メールアドレスが一意である"""
        User.objects.create_user(
            user_id='test001',
            password='testpass123',
            store=self.store,
            email='test@example.com'
        )
        
        from django.db import IntegrityError
        with self.assertRaises(IntegrityError):
            User.objects.create_user(
                user_id='test002',
                password='testpass123',
                store=self.store,
                email='test@example.com'
            )

    def test_user_id_is_primary_key(self):
        """user_idがプライマリーキーである"""
        user = User.objects.create_user(
            user_id='test001',
            password='testpass123',
            store=self.store
        )
        self.assertEqual(user.pk, 'test001')

    def test_user_store_relation(self):
        """ユーザーと店舗の関連が正しく設定される"""
        user = User.objects.create_user(
            user_id='test001',
            password='testpass123',
            store=self.store
        )
        self.assertEqual(user.store, self.store)
        self.assertIn(user, self.store.users.all())

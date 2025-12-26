from django.test import TestCase
from django.contrib.auth import get_user_model
from accounts.forms import LoginForm, SignupForm, StaffEditForm
from stores.models import Store

User = get_user_model()


class LoginFormTest(TestCase):
    """LoginFormのテスト"""

    def setUp(self):
        """テストデータの準備"""
        self.store = Store.objects.create(
            store_name='テスト店舗',
            address='テスト住所'
        )
        self.user = User.objects.create_user(
            user_id='test001',
            password='testpass123',
            store=self.store
        )

    def test_login_form_valid_data(self):
        """有効なデータでフォームが通る"""
        form = LoginForm(data={
            'username': 'test001',
            'password': 'testpass123'
        })
        self.assertTrue(form.is_valid())

    def test_login_form_invalid_password(self):
        """無効なパスワードでバリデーションエラーが発生する"""
        form = LoginForm(data={
            'username': 'test001',
            'password': 'wrongpassword'
        })
        self.assertFalse(form.is_valid())
        self.assertIn('ID or password is incorrect', str(form.errors))

    def test_login_form_invalid_username(self):
        """存在しないユーザー名でバリデーションエラーが発生する"""
        form = LoginForm(data={
            'username': 'nonexistent',
            'password': 'testpass123'
        })
        self.assertFalse(form.is_valid())
        self.assertIn('ID or password is incorrect', str(form.errors))

    def test_login_form_inactive_user(self):
        """無効化されたユーザーでバリデーションエラーが発生する"""
        self.user.is_active = False
        self.user.save()
        
        form = LoginForm(data={
            'username': 'test001',
            'password': 'testpass123'
        })
        self.assertFalse(form.is_valid())
        # 非アクティブユーザーの場合、認証に失敗してエラーメッセージが返る
        self.assertIn('ID or password is incorrect', str(form.errors))

    def test_login_form_get_user_method(self):
        """get_userメソッドが正しいユーザーを返す"""
        form = LoginForm(data={
            'username': 'test001',
            'password': 'testpass123'
        })
        self.assertTrue(form.is_valid())
        self.assertEqual(form.get_user(), self.user)

    def test_login_form_missing_username(self):
        """ユーザー名なしでバリデーションエラーが発生する"""
        form = LoginForm(data={
            'password': 'testpass123'
        })
        self.assertFalse(form.is_valid())

    def test_login_form_missing_password(self):
        """パスワードなしでバリデーションエラーが発生する"""
        form = LoginForm(data={
            'username': 'test001'
        })
        self.assertFalse(form.is_valid())


class SignupFormTest(TestCase):
    """SignupFormのテスト"""

    def setUp(self):
        """テストデータの準備"""
        self.store = Store.objects.create(
            store_name='テスト店舗',
            address='テスト住所'
        )

    def test_signup_form_valid_data(self):
        """有効なデータでフォームが通る"""
        form = SignupForm(data={
            'user_id': 'test001',
            'last_name': '山田',
            'first_name': '太郎',
            'email': 'test@example.com',
            'password': 'testpass123',
            'store': self.store.pk,
            'user_type': 'staff'
        })
        self.assertTrue(form.is_valid())

    def test_signup_form_saves_user(self):
        """フォーム保存でユーザーが作成される"""
        form = SignupForm(data={
            'user_id': 'test001',
            'last_name': '山田',
            'first_name': '太郎',
            'email': 'test@example.com',
            'password': 'testpass123',
            'store': self.store.pk,
            'user_type': 'staff'
        })
        self.assertTrue(form.is_valid())
        user = form.save()
        
        self.assertEqual(user.user_id, 'test001')
        self.assertEqual(User.objects.count(), 1)

    def test_signup_form_hashes_password(self):
        """パスワードがハッシュ化されて保存される"""
        form = SignupForm(data={
            'user_id': 'test001',
            'last_name': '山田',
            'first_name': '太郎',
            'email': 'test@example.com',
            'password': 'testpass123',
            'store': self.store.pk,
            'user_type': 'staff'
        })
        self.assertTrue(form.is_valid())
        user = form.save()
        
        self.assertTrue(user.check_password('testpass123'))
        self.assertNotEqual(user.password, 'testpass123')

    def test_signup_form_missing_required_field(self):
        """必須フィールドなしでバリデーションエラーが発生する"""
        form = SignupForm(data={
            'last_name': '山田',
            'first_name': '太郎',
            'email': 'test@example.com',
            'password': 'testpass123',
            'store': self.store.pk
        })
        self.assertFalse(form.is_valid())

    def test_signup_form_invalid_email(self):
        """無効なメールアドレスでバリデーションエラーが発生する"""
        form = SignupForm(data={
            'user_id': 'test001',
            'last_name': '山田',
            'first_name': '太郎',
            'email': 'invalid-email',
            'password': 'testpass123',
            'store': self.store.pk,
            'user_type': 'staff'
        })
        self.assertFalse(form.is_valid())


class StaffEditFormTest(TestCase):
    """StaffEditFormのテスト"""

    def setUp(self):
        """テストデータの準備"""
        self.store1 = Store.objects.create(
            store_name='テスト店舗1',
            address='テスト住所1'
        )
        self.store2 = Store.objects.create(
            store_name='テスト店舗2',
            address='テスト住所2'
        )
        self.user = User.objects.create_user(
            user_id='test001',
            password='testpass123',
            store=self.store1,
            first_name='太郎',
            last_name='山田'
        )

    def test_staff_edit_form_valid_data(self):
        """有効なデータでフォームが通る"""
        form = StaffEditForm(
            data={
                'last_name': '田中',
                'first_name': '次郎',
                'user_type': 'manager',
                'store': self.store2.pk
            },
            instance=self.user
        )
        self.assertTrue(form.is_valid())

    def test_staff_edit_form_updates_user(self):
        """フォーム保存でユーザー情報が更新される"""
        form = StaffEditForm(
            data={
                'last_name': '田中',
                'first_name': '次郎',
                'user_type': 'manager',
                'store': self.store2.pk
            },
            instance=self.user
        )
        self.assertTrue(form.is_valid())
        updated_user = form.save()
        
        self.assertEqual(updated_user.last_name, '田中')
        self.assertEqual(updated_user.first_name, '次郎')
        self.assertEqual(updated_user.user_type, 'manager')
        self.assertEqual(updated_user.store, self.store2)

    def test_staff_edit_form_only_editable_fields(self):
        """編集可能なフィールドのみが含まれる"""
        form = StaffEditForm(instance=self.user)
        self.assertIn('last_name', form.fields)
        self.assertIn('first_name', form.fields)
        self.assertIn('user_type', form.fields)
        self.assertIn('store', form.fields)
        self.assertNotIn('user_id', form.fields)
        self.assertNotIn('password', form.fields)

    def test_staff_edit_form_missing_required_field(self):
        """必須フィールドなしでバリデーションエラーが発生する"""
        form = StaffEditForm(
            data={
                'last_name': '田中',
                'first_name': '次郎'
            },
            instance=self.user
        )
        self.assertFalse(form.is_valid())

from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth import get_user_model
from stores.models import Store

User = get_user_model()


class LoginViewTest(TestCase):
    """login_viewのテスト"""

    def setUp(self):
        """テストデータの準備"""
        self.client = Client()
        self.store = Store.objects.create(
            store_name='テスト店舗',
            address='テスト住所'
        )
        self.user = User.objects.create_user(
            user_id='test001',
            password='testpass123',
            store=self.store
        )
        self.url = reverse('accounts:login')

    def test_login_view_get_returns_200(self):
        """GETリクエストで200が返る"""
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)

    def test_login_view_uses_correct_template(self):
        """正しいテンプレートが使用される"""
        response = self.client.get(self.url)
        self.assertTemplateUsed(response, 'accounts/login.html')

    def test_login_view_authenticated_user_redirects(self):
        """認証済みユーザーはリダイレクトされる"""
        self.client.login(username='test001', password='testpass123')
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('common:index'))

    def test_login_view_post_valid_credentials(self):
        """有効な認証情報でログインできる"""
        response = self.client.post(self.url, {
            'username': 'test001',
            'password': 'testpass123'
        })
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('common:index'))

    def test_login_view_post_invalid_credentials(self):
        """無効な認証情報でログインできない"""
        response = self.client.post(self.url, {
            'username': 'test001',
            'password': 'wrongpassword'
        })
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'accounts/login.html')


class LogoutViewTest(TestCase):
    """logout_viewのテスト"""

    def setUp(self):
        """テストデータの準備"""
        self.client = Client()
        self.store = Store.objects.create(
            store_name='テスト店舗',
            address='テスト住所'
        )
        self.user = User.objects.create_user(
            user_id='test001',
            password='testpass123',
            store=self.store
        )
        self.url = reverse('accounts:logout')

    def test_logout_view_redirects_to_login(self):
        """ログアウト後にログインページにリダイレクトされる"""
        self.client.login(username='test001', password='testpass123')
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('accounts:login'))


class ProfileViewTest(TestCase):
    """profile_viewのテスト"""

    def setUp(self):
        """テストデータの準備"""
        self.client = Client()
        self.store = Store.objects.create(
            store_name='テスト店舗',
            address='テスト住所'
        )
        self.user = User.objects.create_user(
            user_id='test001',
            password='testpass123',
            store=self.store,
            first_name='太郎',
            last_name='山田'
        )
        self.url = reverse('accounts:profile')

    def test_profile_view_requires_login(self):
        """未認証ユーザーはログインページにリダイレクトされる"""
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 302)
        self.assertIn('/accounts/login/', response.url)

    def test_profile_view_returns_200_for_authenticated_user(self):
        """認証済みユーザーには200が返る"""
        self.client.login(username='test001', password='testpass123')
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)

    def test_profile_view_uses_correct_template(self):
        """正しいテンプレートが使用される"""
        self.client.login(username='test001', password='testpass123')
        response = self.client.get(self.url)
        self.assertTemplateUsed(response, 'accounts/profile.html')

    def test_profile_view_context_contains_user_info(self):
        """コンテキストにユーザー情報が含まれる"""
        self.client.login(username='test001', password='testpass123')
        response = self.client.get(self.url)
        self.assertIn('full_name', response.context)
        self.assertIn('user_id', response.context)
        self.assertIn('role', response.context)
        self.assertIn('store_name', response.context)

    def test_profile_view_displays_full_name(self):
        """フルネームが正しく表示される"""
        self.client.login(username='test001', password='testpass123')
        response = self.client.get(self.url)
        self.assertEqual(response.context['full_name'], '山田 太郎')


class SignupViewTest(TestCase):
    """signup_viewのテスト"""

    def setUp(self):
        """テストデータの準備"""
        self.client = Client()
        self.store = Store.objects.create(
            store_name='テスト店舗',
            address='テスト住所'
        )
        self.admin_user = User.objects.create_user(
            user_id='admin001',
            password='adminpass123',
            store=self.store,
            user_type='admin'
        )
        self.staff_user = User.objects.create_user(
            user_id='staff001',
            password='staffpass123',
            store=self.store,
            user_type='staff'
        )
        self.url = reverse('accounts:signup')

    def test_signup_view_requires_login(self):
        """未認証ユーザーはログインページにリダイレクトされる"""
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 302)

    def test_signup_view_requires_admin_permission(self):
        """スタッフユーザーはアクセスできない"""
        self.client.login(username='staff001', password='staffpass123')
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 403)

    def test_signup_view_admin_can_access(self):
        """管理者はアクセスできる"""
        self.client.login(username='admin001', password='adminpass123')
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)

    def test_signup_view_uses_correct_template(self):
        """正しいテンプレートが使用される"""
        self.client.login(username='admin001', password='adminpass123')
        response = self.client.get(self.url)
        self.assertTemplateUsed(response, 'accounts/signup.html')

    def test_signup_view_post_creates_user(self):
        """POSTリクエストでユーザーが作成される"""
        self.client.login(username='admin001', password='adminpass123')
        response = self.client.post(self.url, {
            'user_id': 'newuser001',
            'last_name': '鈴木',
            'first_name': '花子',
            'email': 'newuser@example.com',
            'password': 'newpass123',
            'store': self.store.pk,
            'user_type': 'staff'
        })
        self.assertEqual(response.status_code, 302)
        self.assertTrue(User.objects.filter(user_id='newuser001').exists())


class StaffListViewTest(TestCase):
    """staff_list_viewのテスト"""

    def setUp(self):
        """テストデータの準備"""
        self.client = Client()
        self.store = Store.objects.create(
            store_name='テスト店舗',
            address='テスト住所'
        )
        self.manager_user = User.objects.create_user(
            user_id='manager001',
            password='managerpass123',
            store=self.store,
            user_type='manager'
        )
        self.staff_user = User.objects.create_user(
            user_id='staff001',
            password='staffpass123',
            store=self.store,
            user_type='staff'
        )
        self.url = reverse('accounts:staff_list')

    def test_staff_list_view_requires_login(self):
        """未認証ユーザーはログインページにリダイレクトされる"""
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 302)

    def test_staff_list_view_requires_manager_permission(self):
        """スタッフユーザーはリダイレクトされる"""
        self.client.login(username='staff001', password='staffpass123')
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('common:index'))

    def test_staff_list_view_manager_can_access(self):
        """店長はアクセスできる"""
        self.client.login(username='manager001', password='managerpass123')
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)

    def test_staff_list_view_uses_correct_template(self):
        """正しいテンプレートが使用される"""
        self.client.login(username='manager001', password='managerpass123')
        response = self.client.get(self.url)
        self.assertTemplateUsed(response, 'accounts/staff_list.html')

    def test_staff_list_view_context_contains_users(self):
        """コンテキストにユーザー一覧が含まれる"""
        self.client.login(username='manager001', password='managerpass123')
        response = self.client.get(self.url)
        self.assertIn('users', response.context)


class StaffEditViewTest(TestCase):
    """staff_edit_viewのテスト"""

    def setUp(self):
        """テストデータの準備"""
        self.client = Client()
        self.store = Store.objects.create(
            store_name='テスト店舗',
            address='テスト住所'
        )
        self.manager_user = User.objects.create_user(
            user_id='manager001',
            password='managerpass123',
            store=self.store,
            user_type='manager'
        )
        self.staff_user = User.objects.create_user(
            user_id='staff001',
            password='staffpass123',
            store=self.store,
            user_type='staff',
            first_name='太郎',
            last_name='山田'
        )
        self.url = reverse('accounts:staff_edit', args=['staff001'])

    def test_staff_edit_view_requires_login(self):
        """未認証ユーザーはログインページにリダイレクトされる"""
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 302)

    def test_staff_edit_view_requires_manager_permission(self):
        """スタッフユーザーはリダイレクトされる"""
        self.client.login(username='staff001', password='staffpass123')
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('common:index'))

    def test_staff_edit_view_manager_can_access(self):
        """店長はアクセスできる"""
        self.client.login(username='manager001', password='managerpass123')
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)

    def test_staff_edit_view_uses_correct_template(self):
        """正しいテンプレートが使用される"""
        self.client.login(username='manager001', password='managerpass123')
        response = self.client.get(self.url)
        self.assertTemplateUsed(response, 'accounts/staff_edit.html')

    def test_staff_edit_view_nonexistent_user_returns_404(self):
        """存在しないユーザーの場合404が返る"""
        self.client.login(username='manager001', password='managerpass123')
        url = reverse('accounts:staff_edit', args=['nonexistent'])
        response = self.client.get(url)
        self.assertEqual(response.status_code, 404)

    def test_staff_edit_view_post_updates_user(self):
        """POSTリクエストでユーザー情報が更新される"""
        self.client.login(username='manager001', password='managerpass123')
        response = self.client.post(self.url, {
            'last_name': '田中',
            'first_name': '次郎',
            'user_type': 'manager',
            'store': self.store.pk
        })
        self.assertEqual(response.status_code, 302)
        
        self.staff_user.refresh_from_db()
        self.assertEqual(self.staff_user.last_name, '田中')
        self.assertEqual(self.staff_user.first_name, '次郎')

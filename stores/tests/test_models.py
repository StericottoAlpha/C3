from django.test import TestCase
from django.contrib.auth import get_user_model
from django.utils import timezone
from django.db import IntegrityError
from stores.models import Store, MonthlyGoal

User = get_user_model()


class StoreModelTest(TestCase):
    """Storeモデルのテスト"""

    def setUp(self):
        """テストデータの準備"""
        self.store = Store.objects.create(
            store_name='テスト店舗',
            address='東京都渋谷区'
        )
        self.user = User.objects.create_user(
            user_id='manager001',
            password='testpass123',
            store=self.store,
            user_type='manager'
        )

    def test_store_creation_with_required_fields(self):
        """必須フィールドで店舗が作成できる"""
        store = Store.objects.create(
            store_name='新規店舗',
            address='東京都新宿区'
        )
        self.assertIsNotNone(store)
        self.assertEqual(store.store_name, '新規店舗')
        self.assertEqual(store.address, '東京都新宿区')

    def test_store_str_method(self):
        """__str__メソッドが正しく動作する"""
        self.assertEqual(str(self.store), 'テスト店舗')

    def test_store_manager_can_be_null(self):
        """managerフィールドはnullが許可される"""
        store = Store.objects.create(
            store_name='管理者なし店舗',
            address='東京都港区'
        )
        self.assertIsNone(store.manager)

    def test_store_manager_can_be_set(self):
        """managerフィールドにユーザーを設定できる"""
        self.store.manager = self.user
        self.store.save()
        self.assertEqual(self.store.manager, self.user)

    def test_store_created_at_is_set_automatically(self):
        """created_atが自動的に設定される"""
        self.assertIsNotNone(self.store.created_at)
        self.assertIsInstance(self.store.created_at, timezone.datetime)

    def test_store_id_is_primary_key(self):
        """store_idがプライマリーキーである"""
        self.assertEqual(self.store.pk, self.store.store_id)

    def test_store_manager_set_null_on_delete(self):
        """ユーザー削除時にmanagerがNULLになる"""
        self.store.manager = self.user
        self.store.save()
        self.user.delete()
        self.store.refresh_from_db()
        self.assertIsNone(self.store.manager)

    def test_store_users_relation(self):
        """店舗とユーザーの関連が正しく設定される"""
        self.assertIn(self.user, self.store.users.all())

    def test_store_managed_stores_relation(self):
        """managerとmanaged_storesの関連が正しく設定される"""
        self.store.manager = self.user
        self.store.save()
        self.assertIn(self.store, self.user.managed_stores.all())


class MonthlyGoalModelTest(TestCase):
    """MonthlyGoalモデルのテスト"""

    def setUp(self):
        """テストデータの準備"""
        self.store = Store.objects.create(
            store_name='テスト店舗',
            address='東京都渋谷区'
        )

    def test_monthly_goal_creation_with_required_fields(self):
        """必須フィールドで月次目標が作成できる"""
        goal = MonthlyGoal.objects.create(
            store=self.store,
            year=2025,
            month=12,
            goal_text='売上目標: 1000万円'
        )
        self.assertIsNotNone(goal)
        self.assertEqual(goal.store, self.store)
        self.assertEqual(goal.year, 2025)
        self.assertEqual(goal.month, 12)

    def test_monthly_goal_default_achievement_rate_is_zero(self):
        """デフォルトのachievement_rateが0である"""
        goal = MonthlyGoal.objects.create(
            store=self.store,
            year=2025,
            month=12,
            goal_text='売上目標'
        )
        self.assertEqual(goal.achievement_rate, 0)

    def test_monthly_goal_default_achievement_text_is_empty(self):
        """デフォルトのachievement_textが空文字列である"""
        goal = MonthlyGoal.objects.create(
            store=self.store,
            year=2025,
            month=12,
            goal_text='売上目標'
        )
        self.assertEqual(goal.achievement_text, '')

    def test_monthly_goal_str_method(self):
        """__str__メソッドが正しく動作する"""
        goal = MonthlyGoal.objects.create(
            store=self.store,
            year=2025,
            month=12,
            goal_text='売上目標'
        )
        self.assertEqual(str(goal), 'テスト店舗 - 2025年12月')

    def test_monthly_goal_created_at_is_set_automatically(self):
        """created_atが自動的に設定される"""
        goal = MonthlyGoal.objects.create(
            store=self.store,
            year=2025,
            month=12,
            goal_text='売上目標'
        )
        self.assertIsNotNone(goal.created_at)
        self.assertIsInstance(goal.created_at, timezone.datetime)

    def test_monthly_goal_updated_at_is_set_automatically(self):
        """updated_atが自動的に設定される"""
        goal = MonthlyGoal.objects.create(
            store=self.store,
            year=2025,
            month=12,
            goal_text='売上目標'
        )
        self.assertIsNotNone(goal.updated_at)
        self.assertIsInstance(goal.updated_at, timezone.datetime)

    def test_monthly_goal_updated_at_changes_on_save(self):
        """保存時にupdated_atが更新される"""
        goal = MonthlyGoal.objects.create(
            store=self.store,
            year=2025,
            month=12,
            goal_text='売上目標'
        )
        old_updated_at = goal.updated_at
        
        import time
        time.sleep(0.01)  # わずかに時間を置く
        
        goal.achievement_rate = 50
        goal.save()
        goal.refresh_from_db()
        
        self.assertGreater(goal.updated_at, old_updated_at)

    def test_monthly_goal_goal_id_is_primary_key(self):
        """goal_idがプライマリーキーである"""
        goal = MonthlyGoal.objects.create(
            store=self.store,
            year=2025,
            month=12,
            goal_text='売上目標'
        )
        self.assertEqual(goal.pk, goal.goal_id)

    def test_monthly_goal_store_relation(self):
        """月次目標と店舗の関連が正しく設定される"""
        goal = MonthlyGoal.objects.create(
            store=self.store,
            year=2025,
            month=12,
            goal_text='売上目標'
        )
        self.assertEqual(goal.store, self.store)
        self.assertIn(goal, self.store.monthly_goals.all())

    def test_monthly_goal_cascade_delete_on_store_delete(self):
        """店舗削除時に月次目標も削除される"""
        goal = MonthlyGoal.objects.create(
            store=self.store,
            year=2025,
            month=12,
            goal_text='売上目標'
        )
        goal_id = goal.goal_id
        self.store.delete()
        self.assertFalse(MonthlyGoal.objects.filter(goal_id=goal_id).exists())

    def test_monthly_goal_unique_together_constraint(self):
        """同じ店舗・年・月の組み合わせは一意である"""
        MonthlyGoal.objects.create(
            store=self.store,
            year=2025,
            month=12,
            goal_text='売上目標'
        )
        
        with self.assertRaises(IntegrityError):
            MonthlyGoal.objects.create(
                store=self.store,
                year=2025,
                month=12,
                goal_text='別の目標'
            )

    def test_monthly_goal_ordering(self):
        """月次目標が年月の降順でソートされる"""
        MonthlyGoal.objects.create(
            store=self.store,
            year=2025,
            month=11,
            goal_text='11月目標'
        )
        MonthlyGoal.objects.create(
            store=self.store,
            year=2025,
            month=12,
            goal_text='12月目標'
        )
        MonthlyGoal.objects.create(
            store=self.store,
            year=2024,
            month=12,
            goal_text='2024年12月目標'
        )
        
        goals = MonthlyGoal.objects.all()
        self.assertEqual(goals[0].year, 2025)
        self.assertEqual(goals[0].month, 12)
        self.assertEqual(goals[1].year, 2025)
        self.assertEqual(goals[1].month, 11)
        self.assertEqual(goals[2].year, 2024)
        self.assertEqual(goals[2].month, 12)

    def test_monthly_goal_with_achievement_rate(self):
        """達成率付きで月次目標が作成できる"""
        goal = MonthlyGoal.objects.create(
            store=self.store,
            year=2025,
            month=12,
            goal_text='売上目標',
            achievement_rate=75
        )
        self.assertEqual(goal.achievement_rate, 75)

    def test_monthly_goal_with_achievement_text(self):
        """達成状況テキスト付きで月次目標が作成できる"""
        goal = MonthlyGoal.objects.create(
            store=self.store,
            year=2025,
            month=12,
            goal_text='売上目標',
            achievement_text='順調に推移しています'
        )
        self.assertEqual(goal.achievement_text, '順調に推移しています')

    def test_monthly_goal_different_stores_same_period(self):
        """異なる店舗であれば同じ年月で作成できる"""
        store2 = Store.objects.create(
            store_name='別の店舗',
            address='東京都新宿区'
        )
        
        goal1 = MonthlyGoal.objects.create(
            store=self.store,
            year=2025,
            month=12,
            goal_text='店舗1の目標'
        )
        goal2 = MonthlyGoal.objects.create(
            store=store2,
            year=2025,
            month=12,
            goal_text='店舗2の目標'
        )
        
        self.assertNotEqual(goal1.goal_id, goal2.goal_id)
        self.assertEqual(MonthlyGoal.objects.filter(year=2025, month=12).count(), 2)

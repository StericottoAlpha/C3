from django.test import TestCase
from django.contrib.auth import get_user_model
from datetime import datetime, timedelta, date
from stores.models import Store, MonthlyGoal
from reports.models import StoreDailyPerformance, DailyReport
from analytics.services import AnalyticsService

User = get_user_model()

class AnalyticsServiceTest(TestCase):
    def setUp(self):
        self.store = Store.objects.create(
            store_name='A店',
            address='東京都渋谷区道玄坂1-2-3',
            store_id=1
        )
        
     
        self.staff = User.objects.create_user(
            user_id='staff001',
            password='password123',
            last_name='田中',
            first_name='花子',
            store=self.store  # ← ここが必須でした
        )
        
        self.today = datetime.now().date()
        self.create_test_data()

    def create_test_data(self):
        # 過去7日間の売上データ
        for i in range(7):
            d = self.today - timedelta(days=6-i)
            StoreDailyPerformance.objects.create(
                store=self.store,
                date=d,
                sales_amount=100000 + (i * 10000),
                customer_count=50 + (i * 5),
                cash_difference=0
            )
            # インシデントデータ (偶数日のみ)
            if i % 2 == 0:
                DailyReport.objects.create(
                    store=self.store,
                    user=self.staff,
                    date=d,
                    genre='claim',
                    location='hall',
                    title=f'インシデント{i}',
                    content=f'テスト{i}'
                )

        # 月次目標データ
        MonthlyGoal.objects.create(
            store=self.store,
            year=self.today.year,
            month=self.today.month,
            goal_text="売上1000万",
            achievement_rate=80,
            achievement_text="順調"
        )

    def test_get_sales_data(self):
        """売上データの取得テスト"""
        start_date = self.today - timedelta(days=6)
        result = AnalyticsService.get_sales_data(self.store, start_date, self.today)
        self.assertEqual(len(result['labels']), 7)
        self.assertEqual(result['data'][0], 100000)
        self.assertEqual(result['data'][-1], 160000)

    def test_get_customer_count_data(self):
        """客数データの取得テスト"""
        start_date = self.today - timedelta(days=6)
        result = AnalyticsService.get_customer_count_data(self.store, start_date, self.today)
        self.assertEqual(result['data'][0], 50)
        self.assertEqual(result['data'][-1], 80)

    def test_get_incident_by_location_data(self):
        """場所別インシデント集計テスト"""
        start_date = self.today - timedelta(days=6)
        result = AnalyticsService.get_incident_by_location_data(self.store, start_date, self.today)
        
        self.assertIn('datasets', result)
        hall_data = next(d for d in result['datasets'] if d['label'] == 'ホール')
        self.assertGreaterEqual(sum(hall_data['data']), 4)

    def test_get_monthly_goal_data(self):
        """月次目標取得テスト"""
        data = AnalyticsService.get_monthly_goal_data(self.store, self.today.year, self.today.month)
        self.assertEqual(data['goal_text'], "売上1000万")
        self.assertEqual(data['achievement_rate'], 80)

    def test_get_monthly_goal_data_empty(self):
        """存在しない月の目標取得テスト"""
        data = AnalyticsService.get_monthly_goal_data(self.store, 2099, 1)
        self.assertEqual(data['goal_text'], "目標が設定されていません")

    def test_calculate_period_dates(self):
        """期間計算ロジックのテスト"""
        s, e, label = AnalyticsService.calculate_period_dates('week', 0)
        self.assertLessEqual(s, self.today)
        self.assertGreaterEqual(e, self.today)
        
        s, e, label = AnalyticsService.calculate_period_dates('month', -1)
        expected_prev_month = (self.today.replace(day=1) - timedelta(days=1)).month
        self.assertEqual(s.month, expected_prev_month)

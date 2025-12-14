from django.test import TestCase
from django.contrib.auth import get_user_model
from datetime import datetime, timedelta
from stores.models import Store
from reports.models import StoreDailyPerformance, DailyReport
from analytics.services import AnalyticsService

User = get_user_model()


class AnalyticsServiceTest(TestCase):
    def setUp(self):
        self.store = Store.objects.create(
            store_name='A店',
            address='東京都渋谷区道玄坂1-2-3',
            sales_target='月間売上目標: 500万円'
        )
        
        self.staff = User.objects.create_user(
            user_id='staff001',
            password='password123',
            last_name='田中',
            first_name='花子',
            store=self.store,
            user_type='staff',
            email='staff@example.com'
        )
        
        self.today = datetime.now().date()
        self.create_test_data()

    def create_test_data(self):
        for i in range(7):
            date = self.today - timedelta(days=6-i)
            StoreDailyPerformance.objects.create(
                store=self.store,
                date=date,
                sales_amount=100000 + (i * 10000),
                customer_count=50 + (i * 5),
                cash_difference=0,
                registered_by=None
            )
            for j in range(2 if i % 2 == 1 else 1):
                DailyReport.objects.create(
                    store=self.store,
                    user=self.staff,
                    date=date,
                    genre='claim',
                    location='hall',
                    title=f'インシデント{i}-{j}',
                    content=f'テスト{i}-{j}',
                    post_to_bbs=False
                )

    def test_get_sales_data(self):
        start_date = self.today - timedelta(days=6)
        end_date = self.today
        result = AnalyticsService.get_sales_data(self.store, start_date, end_date)
        self.assertEqual(len(result['labels']), 7)
        self.assertEqual(len(result['data']), 7)
        expected_sales = [100000, 110000, 120000, 130000, 140000, 150000, 160000]
        self.assertEqual(result['data'], expected_sales)

    def test_get_customer_count_data(self):
        start_date = self.today - timedelta(days=6)
        end_date = self.today
        result = AnalyticsService.get_customer_count_data(self.store, start_date, end_date)
        expected_customers = [50, 55, 60, 65, 70, 75, 80]
        self.assertEqual(result['data'], expected_customers)

    def test_get_incident_count_data(self):
        start_date = self.today - timedelta(days=6)
        end_date = self.today
        result = AnalyticsService.get_incident_count_data(self.store, start_date, end_date)
        expected_incidents = [1, 2, 1, 2, 1, 2, 1]
        self.assertEqual(result['data'], expected_incidents)

    def test_get_week_range(self):
        start_date, end_date = AnalyticsService.get_week_range()
        self.assertEqual((end_date - start_date).days, 6)
        self.assertEqual(start_date.weekday(), 0)
        self.assertEqual(end_date.weekday(), 6)

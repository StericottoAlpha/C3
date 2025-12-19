from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth import get_user_model
from datetime import datetime, timedelta
from stores.models import Store
from reports.models import StoreDailyPerformance, DailyReport
import json

User = get_user_model()


class GraphDataAPITest(TestCase):
    def setUp(self):
        self.store_a = Store.objects.create(
            store_name='A店',
            address='東京都渋谷区道玄坂1-2-3'
        )
        
        self.staff_a = User.objects.create_user(
            user_id='staff001',
            password='password123',
            last_name='田中',
            first_name='花子',
            store=self.store_a,
            user_type='staff',
            email='staff001@example.com'
        )
        
        self.today = datetime.now().date()
        self.create_test_data()
        self.client = Client()

    def create_test_data(self):
        # 先週の月曜日から日曜日までのデータを作成（確実に過去のデータとするため）
        weekday = self.today.weekday()
        this_monday = self.today - timedelta(days=weekday)
        last_monday = this_monday - timedelta(days=7)

        for i in range(7):
            date = last_monday + timedelta(days=i)
            StoreDailyPerformance.objects.create(
                store=self.store_a,
                date=date,
                sales_amount=100000 + (i * 10000),
                customer_count=50 + (i * 5),
                cash_difference=0,
                registered_by=None
            )
            if i % 2 == 0:
                DailyReport.objects.create(
                    store=self.store_a,
                    user=self.staff_a,
                    date=date,
                    genre='claim',
                    location='hall',
                    title=f'クレーム{i}',
                    content=f'テストクレーム{i}',
                    post_to_bbs=False
                )

    def test_sales_graph_weekly(self):
        self.client.login(user_id='staff001', password='password123')
        response = self.client.get(reverse('analytics:graph_data'), {
            'graph_type': 'sales',
            'period': 'week',
            'offset': -1
        })
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content)
        self.assertEqual(data['title'], '売上推移')
        self.assertEqual(len(data['labels']), 7)
        expected_sales = [100000, 110000, 120000, 130000, 140000, 150000, 160000]
        self.assertEqual(data['data'], expected_sales)

    def test_customer_count_graph_weekly(self):
        self.client.login(user_id='staff001', password='password123')
        response = self.client.get(reverse('analytics:graph_data'), {
            'graph_type': 'customer_count',
            'period': 'week',
            'offset': -1
        })
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content)
        expected_customers = [50, 55, 60, 65, 70, 75, 80]
        self.assertEqual(data['data'], expected_customers)

    def test_incident_by_location_graph_weekly(self):
        self.client.login(user_id='staff001', password='password123')
        response = self.client.get(reverse('analytics:graph_data'), {
            'graph_type': 'incident_by_location',
            'period': 'week',
            'offset': -1
        })
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content)
        self.assertIn('datasets', data)
        self.assertIn('labels', data)
        self.assertEqual(len(data['labels']), 7)
        # hallのデータを確認
        hall_dataset = [ds for ds in data['datasets'] if ds['label'] == 'ホール'][0]
        expected_incidents = [1, 0, 1, 0, 1, 0, 1]
        self.assertEqual(hall_dataset['data'], expected_incidents)

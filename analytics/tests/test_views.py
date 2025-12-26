from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth import get_user_model
from datetime import datetime, timedelta
from stores.models import Store, MonthlyGoal
from reports.models import StoreDailyPerformance, DailyReport
import json

User = get_user_model()

class AnalyticsViewTests(TestCase):
    def setUp(self):
        self.store = Store.objects.create(
            store_name='A店',
            address='東京都渋谷区道玄坂1-2-3',
            store_id=99
        )
        
        self.staff = User.objects.create_user(
            user_id='staff001',
            password='password123',
            store=self.store  
        )
        
        self.today = datetime.now().date()
        self.client.login(user_id='staff001', password='password123')
        
        self.create_test_data()

    def create_test_data(self):
        StoreDailyPerformance.objects.create(
            store=self.store,
            date=self.today,
            sales_amount=150000,
            customer_count=80
        )
        self.report = DailyReport.objects.create(
            store=self.store,
            user=self.staff,
            date=self.today,
            genre='claim',
            title='Viewテスト',
            content='詳細'
        )
        MonthlyGoal.objects.create(
            store=self.store,
            year=self.today.year,
            month=self.today.month,
            goal_text="Goal Test"
        )

    def test_dashboard_access(self):
        """ダッシュボードへのアクセス確認"""
        url = reverse('analytics:dashboard')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'analytics/dashboard.html')

    def test_graph_data_api_sales(self):
        """グラフデータAPI (売上)"""
        url = reverse('analytics:graph_data')
        response = self.client.get(url, {
            'graph_type': 'sales',
            'period': 'week',
            'offset': 0
        })
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data['title'], '売上推移')
        self.assertIn('labels', data)

    def test_monthly_goal_api(self):
        """月次目標API"""
        url = reverse('analytics:monthly_goal')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data['goal_text'], "Goal Test")

    def test_calendar_view(self):
        """カレンダー画面"""
        url = reverse('analytics:calendar')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'analytics/calendar.html')

    def test_calendar_day_api(self):
        """カレンダー日付詳細API"""
        ymd = self.today.strftime('%Y-%m-%d')
        url = reverse('analytics:calendar_day_api', args=[ymd])
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertTrue(data['ok'])
        self.assertEqual(data['sales_yen'], 150000)
        self.assertEqual(len(data['items']), 1)

    def test_calendar_detail_view(self):
        """カレンダー詳細画面"""
        url = reverse('analytics:calendar_detail', args=[self.report.pk])
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'analytics/calendar_detail.html')

from django.test import TestCase
from django.contrib.auth import get_user_model
from datetime import datetime, timedelta, date
from unittest.mock import patch
import json
from stores.models import Store, MonthlyGoal
from reports.models import DailyReport, StoreDailyPerformance
from bbs.models import BBSPost
from ai_features.tools.analytics_tools import (
    get_claim_statistics,
    get_sales_trend,
    get_cash_difference_analysis,
    get_report_statistics,
    get_monthly_goal_status,
    gather_topic_related_data,
    compare_periods,
    get_claim_statistics_all_stores,
    get_report_statistics_all_stores,
    gather_topic_related_data_all_stores,
)

User = get_user_model()


class AnalyticsToolsTest(TestCase):
    def setUp(self):
        """テスト用データを作成"""
        self.store1 = Store.objects.create(
            store_id=1,
            store_name='店舗1',
            address='住所1'
        )
        self.store2 = Store.objects.create(
            store_id=2,
            store_name='店舗2',
            address='住所2'
        )

        self.user = User.objects.create_user(
            user_id='testuser',
            password='testpass123',
            store=self.store1
        )

        self.today = datetime.now().date()
        self._create_test_data()

    def _create_test_data(self):
        """テストデータ作成"""
        # 過去7日間のデータ作成
        for i in range(7):
            target_date = self.today - timedelta(days=6-i)

            # 日報データ（クレーム）
            if i % 2 == 0:
                DailyReport.objects.create(
                    store=self.store1,
                    user=self.user,
                    date=target_date,
                    genre='claim',
                    location='hall',
                    title=f'クレーム{i}',
                    content=f'内容{i}'
                )

            # 日報データ（その他）
            DailyReport.objects.create(
                store=self.store1,
                user=self.user,
                date=target_date,
                genre='report',
                location='kitchen',
                title=f'報告{i}',
                content=f'内容{i}'
            )

            # 売上データ
            StoreDailyPerformance.objects.create(
                store=self.store1,
                date=target_date,
                sales_amount=100000 + (i * 10000),
                customer_count=50 + (i * 5),
                cash_difference=100 if i % 2 == 0 else -50
            )

        # 月次目標
        MonthlyGoal.objects.create(
            store=self.store1,
            year=self.today.year,
            month=self.today.month,
            goal_text='月次目標テスト',
            achievement_rate=85,
            achievement_text='順調'
        )

    def test_get_claim_statistics(self):
        """クレーム統計取得のテスト"""
        result_str = get_claim_statistics.invoke({"store_id": self.store1.store_id, "days": 7})
        result = json.loads(result_str)

        self.assertEqual(result['status'], 'success')
        self.assertEqual(result['store_id'], self.store1.store_id)
        self.assertIn('summary', result)
        self.assertIn('claim_count', result['summary'])
        self.assertIn('daily_trend', result)

    def test_get_claim_statistics_no_data(self):
        """データがない店舗のクレーム統計テスト"""
        result_str = get_claim_statistics.invoke({"store_id": self.store2.store_id, "days": 7})
        result = json.loads(result_str)

        self.assertEqual(result['status'], 'success')
        self.assertEqual(result['summary']['claim_count'], 0)

    def test_get_sales_trend(self):
        """売上トレンド取得のテスト"""
        result_str = get_sales_trend.invoke({"store_id": self.store1.store_id, "days": 7})
        result = json.loads(result_str)

        self.assertEqual(result['status'], 'success')
        self.assertIn('summary', result)
        self.assertIn('total_sales', result['summary'])
        self.assertIn('daily_trend', result)

    def test_get_sales_trend_no_data(self):
        """売上データがない場合のテスト"""
        result_str = get_sales_trend.invoke({"store_id": self.store2.store_id, "days": 7})
        result = json.loads(result_str)

        self.assertEqual(result['status'], 'no_data')
        self.assertIn('message', result)

    def test_get_cash_difference_analysis(self):
        """現金過不足分析のテスト"""
        result_str = get_cash_difference_analysis.invoke({"store_id": self.store1.store_id, "days": 7})
        result = json.loads(result_str)

        self.assertEqual(result['status'], 'success')
        self.assertIn('summary', result)
        self.assertIn('total_difference', result['summary'])

    def test_get_cash_difference_analysis_no_data(self):
        """現金過不足データがない場合のテスト"""
        result_str = get_cash_difference_analysis.invoke({"store_id": self.store2.store_id, "days": 7})
        result = json.loads(result_str)

        self.assertEqual(result['status'], 'no_data')
        self.assertIn('message', result)

    def test_get_report_statistics(self):
        """日報統計取得のテスト"""
        result_str = get_report_statistics.invoke({"store_id": self.store1.store_id, "days": 7})
        result = json.loads(result_str)

        self.assertEqual(result['status'], 'success')
        self.assertIn('summary', result)
        self.assertIn('total_reports', result['summary'])
        self.assertIn('genre_breakdown', result)

    def test_get_report_statistics_no_data(self):
        """日報データがない場合のテスト"""
        result_str = get_report_statistics.invoke({"store_id": self.store2.store_id, "days": 7})
        result = json.loads(result_str)

        self.assertEqual(result['status'], 'no_data')
        self.assertIn('message', result)

    def test_get_monthly_goal_status(self):
        """月次目標取得のテスト"""
        result_str = get_monthly_goal_status.invoke({"store_id": self.store1.store_id})
        result = json.loads(result_str)

        self.assertEqual(result['status'], 'success')
        self.assertIn('current_goal', result)
        self.assertEqual(result['current_goal']['goal_text'], '月次目標テスト')

    def test_get_monthly_goal_status_no_goal(self):
        """月次目標がない場合のテスト"""
        result_str = get_monthly_goal_status.invoke({"store_id": self.store2.store_id})
        result = json.loads(result_str)

        self.assertEqual(result['status'], 'no_data')
        self.assertIn('message', result)

    def test_gather_topic_related_data(self):
        """トピック関連データ収集のテスト"""
        result_str = gather_topic_related_data.invoke({
            "topic": "クレーム",
            "store_id": self.store1.store_id,
            "days": 7
        })
        result = json.loads(result_str)

        self.assertEqual(result['status'], 'success')
        self.assertIn('data_sources', result)
        self.assertIn('daily_reports', result['data_sources'])

    def test_gather_topic_related_data_no_results(self):
        """トピック関連データが見つからない場合のテスト"""
        result_str = gather_topic_related_data.invoke({
            "topic": "存在しないトピック",
            "store_id": self.store1.store_id,
            "days": 7
        })
        result = json.loads(result_str)

        self.assertEqual(result['status'], 'success')

    def test_compare_periods(self):
        """期間比較のテスト"""
        result_str = compare_periods.invoke({
            "store_id": self.store1.store_id,
            "metric": "sales",
            "period1_days": 3,
            "period2_days": 6
        })
        result = json.loads(result_str)

        self.assertEqual(result['status'], 'success')
        self.assertIn('period1', result)
        self.assertIn('period2', result)

    def test_compare_periods_claims(self):
        """クレーム比較のテスト"""
        result_str = compare_periods.invoke({
            "store_id": self.store1.store_id,
            "metric": "claims",
            "period1_days": 3,
            "period2_days": 6
        })
        result = json.loads(result_str)

        self.assertEqual(result['status'], 'success')

    def test_compare_periods_invalid_metric(self):
        """無効なメトリックでの期間比較テスト"""
        result_str = compare_periods.invoke({
            "store_id": self.store1.store_id,
            "metric": "invalid_metric",
            "period1_days": 3,
            "period2_days": 6
        })
        result = json.loads(result_str)

        # エラーが返されるか、適切に処理されることを確認
        self.assertIn('status', result)

    def test_get_claim_statistics_all_stores(self):
        """全店舗クレーム統計のテスト"""
        result_str = get_claim_statistics_all_stores.invoke({"days": 7})
        result = json.loads(result_str)

        self.assertEqual(result['status'], 'success')
        self.assertIn('summary', result)
        self.assertIn('store_breakdown', result)

    def test_get_report_statistics_all_stores(self):
        """全店舗日報統計のテスト"""
        result_str = get_report_statistics_all_stores.invoke({"days": 7})
        result = json.loads(result_str)

        self.assertEqual(result['status'], 'success')
        self.assertIn('summary', result)
        self.assertIn('genre_breakdown', result)

    def test_gather_topic_related_data_all_stores(self):
        """全店舗トピック関連データ収集のテスト"""
        result_str = gather_topic_related_data_all_stores.invoke({
            "topic": "クレーム",
            "days": 7
        })
        result = json.loads(result_str)

        self.assertEqual(result['status'], 'success')
        self.assertIn('data_sources', result)
        self.assertIn('daily_reports', result['data_sources'])


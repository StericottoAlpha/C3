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

    def test_get_week_range(self):
        """週の範囲取得テスト"""
        start, end = AnalyticsService.get_week_range()
        # 開始日は終了日の6日前
        self.assertEqual((end - start).days, 6)
        # 週の開始は月曜日
        self.assertEqual(start.weekday(), 0)  # Monday

    def test_get_week_range_with_base_date(self):
        """指定日基準の週の範囲取得テスト"""
        base_date = date(2024, 1, 15)  # This is a Monday
        start, end = AnalyticsService.get_week_range(base_date)
        # 週の開始は月曜日
        self.assertEqual(start.weekday(), 0)
        self.assertEqual((end - start).days, 6)

    def test_get_month_range(self):
        """月の範囲取得テスト"""
        start, end = AnalyticsService.get_month_range()
        # 同じ月である
        self.assertEqual(start.month, end.month)
        self.assertEqual(start.year, end.year)
        # 開始日は1日
        self.assertEqual(start.day, 1)

    def test_get_month_range_with_base_date(self):
        """指定日基準の月の範囲取得テスト"""
        base_date = date(2024, 2, 15)
        start, end = AnalyticsService.get_month_range(base_date)
        self.assertEqual(start, date(2024, 2, 1))
        self.assertEqual(end, date(2024, 2, 29))  # 2024年は閏年

    def test_calculate_period_dates_week_with_offset(self):
        """オフセット付き週の期間計算テスト"""
        start, end, label = AnalyticsService.calculate_period_dates('week', 1)
        # 1週間後
        self.assertEqual((end - start).days, 6)
        self.assertIsNotNone(label)

    def test_get_graph_data_by_type_sales(self):
        """売上グラフデータ取得テスト"""
        start_date = self.today - timedelta(days=6)
        result = AnalyticsService.get_graph_data_by_type(
            'sales',
            self.store,
            start_date,
            self.today
        )
        self.assertIn('title', result)
        self.assertIn('chart_data', result)
        self.assertEqual(result['title'], '売上推移')
        self.assertEqual(len(result['chart_data']['data']), 7)

    def test_get_graph_data_by_type_customer_count(self):
        """客数グラフデータ取得テスト"""
        start_date = self.today - timedelta(days=6)
        result = AnalyticsService.get_graph_data_by_type(
            'customer_count',
            self.store,
            start_date,
            self.today
        )
        self.assertIn('title', result)
        self.assertEqual(result['title'], '客数推移')
        self.assertIn('chart_data', result)
        self.assertGreater(len(result['chart_data']['data']), 0)

    def test_get_graph_data_by_type_incident_by_location(self):
        """場所別インシデントグラフデータ取得テスト"""
        start_date = self.today - timedelta(days=6)
        result = AnalyticsService.get_graph_data_by_type(
            'incident_by_location',
            self.store,
            start_date,
            self.today
        )
        self.assertIn('title', result)
        self.assertIn('chart_data', result)
        self.assertIn('datasets', result['chart_data'])
        self.assertGreater(len(result['chart_data']['datasets']), 0)

    def test_get_graph_data_by_type_invalid(self):
        """無効なグラフタイプのテスト"""
        start_date = self.today - timedelta(days=6)
        with self.assertRaises(ValueError):
            AnalyticsService.get_graph_data_by_type(
                'invalid_type',
                self.store,
                start_date,
                self.today
            )

    def test_get_sales_data_no_data(self):
        """売上データがない期間のテスト"""
        # 未来の日付で検索
        future_start = self.today + timedelta(days=10)
        future_end = self.today + timedelta(days=20)
        result = AnalyticsService.get_sales_data(self.store, future_start, future_end)
        # データがない場合、空のリストまたは0が返される
        if len(result['labels']) > 0:
            self.assertTrue(all(v == 0 for v in result['data']))
        else:
            self.assertEqual(len(result['data']), 0)

    def test_get_customer_count_data_no_data(self):
        """客数データがない期間のテスト"""
        future_start = self.today + timedelta(days=10)
        future_end = self.today + timedelta(days=20)
        result = AnalyticsService.get_customer_count_data(self.store, future_start, future_end)
        self.assertTrue(all(v == 0 for v in result['data']))

    def test_get_incident_by_location_with_genre_filter(self):
        """ジャンルフィルタ付きインシデント集計テスト"""
        start_date = self.today - timedelta(days=6)
        result = AnalyticsService.get_incident_by_location_data(
            self.store,
            start_date,
            self.today,
            genre='claim'
        )
        self.assertIn('datasets', result)
        # クレームデータのみが含まれる
        for dataset in result['datasets']:
            self.assertIsNotNone(dataset['data'])

    def test_calculate_period_dates_with_various_offsets(self):
        """様々なオフセットでの期間計算テスト"""
        # 前週
        start, end, label = AnalyticsService.calculate_period_dates('week', -1)
        # 前週なので今週より前
        current_week_start, current_week_end = AnalyticsService.get_week_range(self.today)
        self.assertLess(end, current_week_start)

        # 前月
        start, end, label = AnalyticsService.calculate_period_dates('month', -1)
        # 前月なので今月より前（年をまたぐ場合もある）
        self.assertTrue(
            start.month < self.today.month or
            (start.month > self.today.month and start.year < self.today.year)
        )

    def test_get_graph_data_by_type_with_genre(self):
        """ジャンル指定のグラフデータ取得テスト"""
        start_date = self.today - timedelta(days=6)
        result = AnalyticsService.get_graph_data_by_type(
            'incident_by_location',
            self.store,
            start_date,
            self.today,
            genre='claim'
        )
        self.assertIn('クレーム', result['title'])

    def test_get_incident_by_location_no_genre(self):
        """ジャンル指定なしのインシデント集計テスト"""
        start_date = self.today - timedelta(days=6)
        result = AnalyticsService.get_incident_by_location_data(
            self.store,
            start_date,
            self.today,
            genre=None
        )
        self.assertIn('datasets', result)

    def test_get_month_range_december(self):
        """12月の月範囲取得テスト（年をまたぐケース）"""
        dec_date = date(2023, 12, 15)
        start, end = AnalyticsService.get_month_range(dec_date)
        self.assertEqual(start, date(2023, 12, 1))
        self.assertEqual(end, date(2023, 12, 31))

    def test_get_monthly_goal_data_current_month(self):
        """当月の目標データ取得テスト（デフォルト引数）"""
        data = AnalyticsService.get_monthly_goal_data(self.store)
        # year/monthを指定しない場合は当月のデータ
        self.assertIn('goal_text', data)
        self.assertIn('achievement_rate', data)

    def test_get_sales_data_single_day(self):
        """1日だけの売上データ取得テスト"""
        result = AnalyticsService.get_sales_data(self.store, self.today, self.today)
        self.assertEqual(len(result['labels']), 1)
        self.assertEqual(len(result['data']), 1)

    def test_get_customer_count_data_single_day(self):
        """1日だけの客数データ取得テスト"""
        result = AnalyticsService.get_customer_count_data(self.store, self.today, self.today)
        self.assertEqual(len(result['data']), 1)

    def test_calculate_period_dates_positive_offset(self):
        """正のオフセットでの期間計算テスト"""
        # 来週
        start, end, label = AnalyticsService.calculate_period_dates('week', 1)
        current_week_start, current_week_end = AnalyticsService.get_week_range(self.today)
        self.assertGreater(start, current_week_end)

        # 来月
        start, end, label = AnalyticsService.calculate_period_dates('month', 1)
        self.assertTrue(
            start.month > self.today.month or
            (start.month < self.today.month and start.year > self.today.year)
        )

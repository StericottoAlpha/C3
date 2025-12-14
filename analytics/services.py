from datetime import datetime, timedelta
from django.db.models import Count, Q
from reports.models import StoreDailyPerformance, DailyReport


class AnalyticsService:
    """分析データを集計するサービスクラス"""

    @staticmethod
    def get_sales_data(store, start_date, end_date):
        """売上データを取得

        Args:
            store: 店舗オブジェクト
            start_date: 開始日
            end_date: 終了日

        Returns:
            dict: {labels: [...], data: [...]}
        """
        # 日付範囲内の全日付を生成
        date_range = []
        current_date = start_date
        while current_date <= end_date:
            date_range.append(current_date)
            current_date += timedelta(days=1)

        # 各日付の売上を集計
        labels = []
        data = []
        today = datetime.now().date()

        for date in date_range:
            # 未来の日付はスキップ
            if date > today:
                continue

            perf = StoreDailyPerformance.objects.filter(
                store=store,
                date=date
            ).first()

            labels.append(date.strftime('%m/%d'))
            data.append(perf.sales_amount if perf else 0)

        return {
            'labels': labels,
            'data': data,
        }

    @staticmethod
    def get_customer_count_data(store, start_date, end_date):
        """客数データを取得

        Args:
            store: 店舗オブジェクト
            start_date: 開始日
            end_date: 終了日

        Returns:
            dict: {labels: [...], data: [...]}
        """
        # 日付範囲内の全日付を生成
        date_range = []
        current_date = start_date
        while current_date <= end_date:
            date_range.append(current_date)
            current_date += timedelta(days=1)

        # 各日付の客数を集計
        labels = []
        data = []
        today = datetime.now().date()

        for date in date_range:
            # 未来の日付はスキップ
            if date > today:
                continue

            perf = StoreDailyPerformance.objects.filter(
                store=store,
                date=date
            ).first()

            labels.append(date.strftime('%m/%d'))
            data.append(perf.customer_count if perf else 0)

        return {
            'labels': labels,
            'data': data,
        }

    @staticmethod
    def get_incident_by_location_data(store, start_date, end_date, genre=None):
        """場所別インシデント数データを取得（積み上げ棒グラフ用）

        Args:
            store: 店舗オブジェクト
            start_date: 開始日
            end_date: 終了日
            genre: 絞り込むジャンル（Noneの場合は全ジャンル）

        Returns:
            dict: {labels: [...], datasets: [{label: 'キッチン', data: [...], backgroundColor: ...}, ...]}
        """
        # 日付範囲内の全日付を生成
        date_range = []
        current_date = start_date
        while current_date <= end_date:
            date_range.append(current_date)
            current_date += timedelta(days=1)

        # 場所定義と色
        locations = [
            ('kitchen', 'キッチン', 'rgb(239, 68, 68)'),      # red
            ('hall', 'ホール', 'rgb(59, 130, 246)'),          # blue
            ('cashier', 'レジ', 'rgb(34, 197, 94)'),          # green
            ('toilet', 'トイレ', 'rgb(234, 179, 8)'),         # yellow
            ('other', 'その他', 'rgb(156, 163, 175)'),        # gray
        ]

        labels = []
        datasets = []
        today = datetime.now().date()

        # ラベル（日付）を生成
        for date in date_range:
            if date > today:
                continue
            labels.append(date.strftime('%m/%d'))

        # 全日付・全場所のデータを先に取得
        all_data = {}
        for date in date_range:
            if date > today:
                continue
            all_data[date] = {}
            for location_code, location_label, color in locations:
                query = DailyReport.objects.filter(
                    store=store,
                    date=date,
                    location=location_code
                )
                if genre:
                    query = query.filter(genre=genre)
                all_data[date][location_code] = query.count()

        # 各場所ごとのデータを集計（棒グラフ用）
        for location_code, location_label, color in locations:
            location_data = []
            for date in date_range:
                # 未来の日付はスキップ
                if date > today:
                    continue

                # 事前に取得したデータを使用
                count = all_data[date][location_code]
                location_data.append(count)

            datasets.append({
                'label': location_label,
                'data': location_data,
                'backgroundColor': color,
                'stack': 'bar',  # 棒グラフ用のスタック
            })

        return {
            'labels': labels,
            'datasets': datasets,
        }

    @staticmethod
    def get_week_range(base_date=None):
        """指定日を含む週の開始日と終了日を取得

        Args:
            base_date: 基準日（Noneの場合は今日）

        Returns:
            tuple: (start_date, end_date)
        """
        if base_date is None:
            base_date = datetime.now().date()

        # 週の開始を月曜日とする
        weekday = base_date.weekday()
        start_date = base_date - timedelta(days=weekday)
        end_date = start_date + timedelta(days=6)

        return start_date, end_date

    @staticmethod
    def get_month_range(base_date=None):
        """指定日を含む月の開始日と終了日を取得

        Args:
            base_date: 基準日（Noneの場合は今日）

        Returns:
            tuple: (start_date, end_date)
        """
        if base_date is None:
            base_date = datetime.now().date()

        start_date = base_date.replace(day=1)

        # 次月の1日から1日引いて月末を取得
        if base_date.month == 12:
            end_date = base_date.replace(year=base_date.year + 1, month=1, day=1) - timedelta(days=1)
        else:
            end_date = base_date.replace(month=base_date.month + 1, day=1) - timedelta(days=1)

        return start_date, end_date

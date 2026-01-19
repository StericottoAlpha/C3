from datetime import datetime, timedelta

from reports.models import DailyReport, StoreDailyPerformance
from stores.models import MonthlyGoal, Store
from django.db.models import Sum


# 店舗ごとの折れ線表示に使うシンプルな色パレット
COLOR_PALETTE = [
    'rgb(59, 130, 246)',   # blue
    'rgb(239, 68, 68)',    # red
    'rgb(34, 197, 94)',    # green
    'rgb(168, 85, 247)',   # purple
    'rgb(245, 158, 11)',   # orange
    'rgb(6, 182, 212)',    # teal
    'rgb(99, 102, 241)',   # indigo
    'rgb(220, 38, 38)',    # deep red
]


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
            labels.append(date.strftime('%m/%d'))

        # storeが指定されている場合は従来通り単一ラインを返す
        if store:
            for date in date_range:
                if date > today:
                    continue

                perf = StoreDailyPerformance.objects.filter(
                    store=store,
                    date=date
                ).first()
                data.append(perf.sales_amount if perf else 0)

            return {
                'labels': labels,
                'data': data,
            }

        # store=None のときは店舗ごとの折れ線データを返す
        datasets = []
        # 本部は除外する
        stores = Store.objects.exclude(store_name='本部').order_by('store_id')
        for idx, s in enumerate(stores):
            store_data = []
            for date in date_range:
                if date > today:
                    continue
                perf = StoreDailyPerformance.objects.filter(store=s, date=date).first()
                store_data.append(perf.sales_amount if perf else 0)

            base_color = COLOR_PALETTE[idx % len(COLOR_PALETTE)]
            datasets.append({
                'label': s.store_name,
                'data': store_data,
                'borderColor': base_color,
                'backgroundColor': base_color,
                'tension': 0.3,
                'fill': False,
                'borderWidth': 2,
                'pointRadius': 3,
            })

        return {
            'labels': labels,
            'datasets': datasets,
            'chart_kind': 'line',
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
            labels.append(date.strftime('%m/%d'))

        # storeが指定されている場合は従来通り単一ラインを返す
        if store:
            for date in date_range:
                if date > today:
                    continue

                perf = StoreDailyPerformance.objects.filter(
                    store=store,
                    date=date
                ).first()
                data.append(perf.customer_count if perf else 0)

            return {
                'labels': labels,
                'data': data,
            }

        # store=None のときは店舗ごとの折れ線データを返す
        datasets = []
        # 本部は除外する
        stores = Store.objects.exclude(store_name='本部').order_by('store_id')
        for idx, s in enumerate(stores):
            store_data = []
            for date in date_range:
                if date > today:
                    continue
                perf = StoreDailyPerformance.objects.filter(store=s, date=date).first()
                store_data.append(perf.customer_count if perf else 0)

            base_color = COLOR_PALETTE[idx % len(COLOR_PALETTE)]
            datasets.append({
                'label': s.store_name,
                'data': store_data,
                'borderColor': base_color,
                'backgroundColor': base_color,
                'tension': 0.3,
                'fill': False,
                'borderWidth': 2,
                'pointRadius': 3,
            })

        return {
            'labels': labels,
            'datasets': datasets,
            'chart_kind': 'line',
        }

    @staticmethod
    def get_incident_by_location_data(store, start_date, end_date, genre=None, base_store=None, period='week'):
        """場所別インシデント数データを取得（折れ線グラフに変更 / 比較モード対応）"""
        # 月選択時は週単位で集計
        if period == 'month':
            return AnalyticsService._get_incident_by_location_weekly(
                store, start_date, end_date, genre, base_store
            )

        # 週選択時またはプレビュー時は日付範囲内の全日付を生成
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
            # プレビューモードの場合はラベルを空文字列に
            if period == 'preview':
                labels.append('')
            else:
                labels.append(date.strftime('%m/%d'))

        # 比較モード：base_store が指定され、かつ store が None（全店舗モードのとき）
        if base_store and store is None:
            # 他店舗の数（本部と自店舗を除外）
            other_store_qs = Store.objects.exclude(store_name='本部').exclude(pk=base_store.pk)
            other_store_count = other_store_qs.count()

            # 日付×場所ごとに自店舗と他店舗合計を取得
            self_counts = {}
            other_totals = {}
            for date in date_range:
                if date > today:
                    continue
                self_counts[date] = {}
                other_totals[date] = {}
                for location_code, location_label, color in locations:
                    q_self = DailyReport.objects.filter(date=date, location=location_code, store=base_store)
                    if genre:
                        q_self = q_self.filter(genre=genre)
                    else:
                        # ネガティブジャンル：クレームと事故のみ
                        q_self = q_self.filter(genre__in=['claim', 'accident'])
                    self_counts[date][location_code] = q_self.count()

                    q_other = DailyReport.objects.filter(date=date, location=location_code).exclude(store__store_name='本部').exclude(store=base_store)
                    if genre:
                        q_other = q_other.filter(genre=genre)
                    else:
                        # ネガティブジャンル：クレームと事故のみ
                        q_other = q_other.filter(genre__in=['claim', 'accident'])
                    other_totals[date][location_code] = q_other.count()

            # 差異（自店舗 - 平均）のデータセットを作成（折れ線）
            for location_code, location_label, color in locations:
                diff_series = []
                self_series = []
                other_avg_series = []
                
                for date in date_range:
                    if date > today:
                        continue
                    
                    val_self = self_counts[date][location_code]
                    val_other_total = other_totals[date][location_code]
                    
                    val_avg = 0.0
                    if other_store_count > 0:
                        val_avg = round(val_other_total / other_store_count, 2)
                    
                    # 差異を計算（自店舗 - 平均）
                    diff = round(val_self - val_avg, 2)
                    
                    diff_series.append(diff)
                    self_series.append(val_self)
                    other_avg_series.append(val_avg)

                datasets.append({
                    'label': location_label,
                    'data': diff_series,
                    'borderColor': color,       # 折れ線の色
                    'backgroundColor': color,   # ポイントなどの色
                    'tension': 0,             # 滑らかな線
                    'fill': False,              # 塗りつぶしなし
                    'custom_self': self_series,
                    'custom_avg': other_avg_series,
                })

            return {
                'labels': labels,
                'datasets': datasets,
                'chart_kind': 'line',  # ★折れ線グラフを指定
            }

        # 従来モード：全日付・全場所のデータを先に取得
        all_data = {}
        for date in date_range:
            if date > today:
                continue
            all_data[date] = {}
            for location_code, location_label, color in locations:
                query = DailyReport.objects.filter(
                    date=date,
                    location=location_code
                )
                if store:
                    query = query.filter(store=store)
                else:
                    # 全店舗の際は本部を除外
                    query = query.exclude(store__store_name='本部')
                if genre:
                    query = query.filter(genre=genre)
                else:
                    # ネガティブジャンル：クレームと事故のみ
                    query = query.filter(genre__in=['claim', 'accident'])
                all_data[date][location_code] = query.count()

        # 各場所ごとのデータを集計（折れ線グラフ用）
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
                'borderColor': color,
                'backgroundColor': color,
                'tension': 0.3,
                'fill': False,
            })

        return {
            'labels': labels,
            'datasets': datasets,
            'chart_kind': 'line',  # ★折れ線グラフを指定
        }

    @staticmethod
    def _get_incident_by_location_weekly(store, start_date, end_date, genre=None, base_store=None):
        """場所別インシデント数データを週単位で集計（折れ線グラフに変更）"""
        # 月を週に分割
        weeks = AnalyticsService.split_month_into_weeks(start_date, end_date)

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

        # ラベル（週）を生成
        for week_start, week_end, week_label in weeks:
            # 未来の週はスキップ
            if week_start > today:
                continue
            labels.append(week_label)

        # 比較モード：base_store が指定され、かつ store が None（全店舗モードのとき）
        if base_store and store is None:
            # 他店舗の数（本部と自店舗を除外）
            other_store_qs = Store.objects.exclude(store_name='本部').exclude(pk=base_store.pk)
            other_store_count = other_store_qs.count()

            # 週×場所ごとに自店舗と他店舗合計を取得
            self_counts = {}
            other_totals = {}
            for week_start, week_end, week_label in weeks:
                # 未来の週はスキップ
                if week_start > today:
                    continue
                self_counts[week_label] = {}
                other_totals[week_label] = {}
                for location_code, location_label, color in locations:
                    # 週の範囲内でクエリ
                    q_self = DailyReport.objects.filter(
                        date__gte=week_start,
                        date__lte=min(week_end, today),
                        location=location_code,
                        store=base_store
                    )
                    if genre:
                        q_self = q_self.filter(genre=genre)
                    else:
                        # ネガティブジャンル：クレームと事故のみ
                        q_self = q_self.filter(genre__in=['claim', 'accident'])
                    self_counts[week_label][location_code] = q_self.count()

                    q_other = DailyReport.objects.filter(
                        date__gte=week_start,
                        date__lte=min(week_end, today),
                        location=location_code
                    ).exclude(store__store_name='本部').exclude(store=base_store)
                    if genre:
                        q_other = q_other.filter(genre=genre)
                    else:
                        # ネガティブジャンル：クレームと事故のみ
                        q_other = q_other.filter(genre__in=['claim', 'accident'])
                    other_totals[week_label][location_code] = q_other.count()

            # 差異（自店舗 - 平均）のデータセットを作成（折れ線）
            for location_code, location_label, color in locations:
                diff_series = []
                self_series = []
                other_avg_series = []

                for week_start, week_end, week_label in weeks:
                    if week_start > today:
                        continue
                    
                    val_self = self_counts[week_label][location_code]
                    val_other_total = other_totals[week_label][location_code]
                    
                    val_avg = 0.0
                    if other_store_count > 0:
                        val_avg = round(val_other_total / other_store_count, 2)
                    
                    # 差異を計算
                    diff = round(val_self - val_avg, 2)
                    
                    diff_series.append(diff)
                    self_series.append(val_self)
                    other_avg_series.append(val_avg)

                datasets.append({
                    'label': location_label,
                    'data': diff_series,
                    'borderColor': color,
                    'backgroundColor': color,
                    'tension': 0 ,
                    'fill': False,
                    'custom_self': self_series,
                    'custom_avg': other_avg_series,
                })

            return {
                'labels': labels,
                'datasets': datasets,
                'chart_kind': 'line',  # ★折れ線グラフを指定
            }

        # 従来モード：全週・全場所のデータを先に取得
        all_data = {}
        for week_start, week_end, week_label in weeks:
            if week_start > today:
                continue
            all_data[week_label] = {}
            for location_code, location_label, color in locations:
                query = DailyReport.objects.filter(
                    date__gte=week_start,
                    date__lte=min(week_end, today),
                    location=location_code
                )
                if store:
                    query = query.filter(store=store)
                else:
                    # 全店舗の際は本部を除外
                    query = query.exclude(store__store_name='本部')
                if genre:
                    query = query.filter(genre=genre)
                else:
                    # ネガティブジャンル：クレームと事故のみ
                    query = query.filter(genre__in=['claim', 'accident'])
                all_data[week_label][location_code] = query.count()

        # 各場所ごとのデータを集計（折れ線グラフ用）
        for location_code, location_label, color in locations:
            location_data = []
            for week_start, week_end, week_label in weeks:
                # 未来の週はスキップ
                if week_start > today:
                    continue

                # 事前に取得したデータを使用
                count = all_data[week_label][location_code]
                location_data.append(count)

            datasets.append({
                'label': location_label,
                'data': location_data,
                'borderColor': color,
                'backgroundColor': color,
                'tension': 0.3,
                'fill': False,
            })

        return {
            'labels': labels,
            'datasets': datasets,
            'chart_kind': 'line',  # ★折れ線グラフを指定
        }
    
    @staticmethod
    def get_incident_trend_by_location(store, start_date, end_date, location, genre=None, period='week', base_store=None):
        """特定場所のインシデント推移データを取得（折れ線グラフ用）

        Args:
            store: 店舗オブジェクト
            start_date: 開始日
            end_date: 終了日
            location: 場所コード
            genre: 絞り込むジャンル
            period: 期間タイプ
            base_store: 比較用の自店舗（Noneの場合は比較なし）

        Returns:
            dict: {labels: [...], datasets: [...]}
        """
        today = datetime.now().date()

        # 比較モード判定（base_storeがあり、かつstoreがNoneの場合＝全店舗モード選択時）
        is_compare_mode = (base_store is not None and store is None)

        labels = []
        
        # === データ取得用内部関数 ===
        def get_counts(start, end):
            """指定期間のカウントを取得"""
            # ベースとなるクエリ
            q_base = DailyReport.objects.filter(date__gte=start, date__lte=end)
            if location != 'all':
                q_base = q_base.filter(location=location)
            if genre:
                q_base = q_base.filter(genre=genre)
            
            if is_compare_mode:
                # --- 比較モード ---
                # 1. 自店舗の数値
                val_self = q_base.filter(store=base_store).count()
                
                # 2. 他店舗（本部と自店舗を除く）の合計数値
                q_other = q_base.exclude(store__store_name='本部').exclude(store=base_store)
                val_other_total = q_other.count()
                
                return val_self, val_other_total
            else:
                # --- 通常モード ---
                if store:
                    q_target = q_base.filter(store=store)
                else:
                    # 全店舗指定（比較なし）の場合は本部のみ除外
                    q_target = q_base.exclude(store__store_name='本部')
                
                return q_target.count(), 0

        # === 期間ループ処理 ===
        data_self = []      # 自店舗用（または通常時のメインデータ）
        data_other_total = [] # 他店舗合計用

        if period == 'month':
            # 週単位
            weeks = AnalyticsService.split_month_into_weeks(start_date, end_date)
            for week_start, week_end, week_label in weeks:
                if week_start > today:
                    continue
                labels.append(week_label)
                
                c_self, c_other = get_counts(week_start, min(week_end, today))
                data_self.append(c_self)
                data_other_total.append(c_other)
        else:
            # 日単位（week, preview）
            current_date = start_date
            while current_date <= end_date:
                if current_date <= today:
                    if period == 'preview':
                        labels.append('')
                    else:
                        labels.append(current_date.strftime('%m/%d'))
                    
                    c_self, c_other = get_counts(current_date, current_date)
                    data_self.append(c_self)
                    data_other_total.append(c_other)
                current_date += timedelta(days=1)

        # === 結果構築 ===
        if is_compare_mode:
            # 他店舗数を取得して平均を計算
            other_store_count = Store.objects.exclude(store_name='本部').exclude(pk=base_store.pk).count()
            data_avg = []
            for total in data_other_total:
                if other_store_count > 0:
                    # 小数第1位まで
                    data_avg.append(round(total / other_store_count, 1))
                else:
                    query = query.exclude(store__store_name='本部')
                if genre:
                    query = query.filter(genre=genre)
                else:
                    # ネガティブジャンル：クレームと事故のみ
                    query = query.filter(genre__in=['claim', 'accident'])

                data.append(query.count())

            return {
                'labels': labels,
                'datasets': [
                    {
                        'label': '自店舗',
                        'data': data_self,
                        'borderColor': 'rgb(59, 130, 246)', # Blue
                        'backgroundColor': 'rgb(59, 130, 246)',
                        'tension': 0.3,
                        'fill': False,
                    },
                    {
                        'label': '他店平均',
                        'data': data_avg,
                        'borderColor': 'rgb(156, 163, 175)', # Gray
                        'backgroundColor': 'rgb(156, 163, 175)',
                        'borderDash': [5, 5], # 点線
                        'tension': 0.3,
                        'fill': False,
                    }
                ]
            }
        else:
            # 従来モード（互換性のため data も残すが、datasets を優先）
            return {
                'labels': labels,
                'data': data_self, 
                'datasets': [{
                    'label': '件数',
                    'data': data_self,
                    'borderColor': 'rgb(59, 130, 246)',
                    'backgroundColor': 'rgba(59, 130, 246, 0.1)',
                    'tension': 0.3,
                    'fill': True,
                }]
            }

        # 週選択時は日単位で集計
        date_range = []
        current_date = start_date
        while current_date <= end_date:
            date_range.append(current_date)
            current_date += timedelta(days=1)

        labels = []
        data = []

        for date in date_range:
            if date > today:
                continue
            # プレビューモードの場合はラベルを空文字列に
            if period == 'preview':
                labels.append('')
            else:
                labels.append(date.strftime('%m/%d'))

            query = DailyReport.objects.filter(date=date)
            # 場所フィルタ（'all'の場合は全場所）
            if location != 'all':
                query = query.filter(location=location)
            if store:
                query = query.filter(store=store)
            else:
                query = query.exclude(store__store_name='本部')
            if genre:
                query = query.filter(genre=genre)
            else:
                # ネガティブジャンル：クレームと事故のみ
                query = query.filter(genre__in=['claim', 'accident'])

            data.append(query.count())

        return {
            'labels': labels,
            'data': data,
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

    @staticmethod
    def split_month_into_weeks(start_date, end_date):
        """月の期間を週単位に分割

        Args:
            start_date: 月の開始日
            end_date: 月の終了日

        Returns:
            list: [(week_start, week_end, week_label), ...]
        """
        weeks = []
        current_date = start_date
        week_number = 1

        while current_date <= end_date:
            # 週の開始（月曜日）
            weekday = current_date.weekday()
            week_start = current_date - timedelta(days=weekday)

            # 月の開始日より前の場合は月の開始日に調整
            if week_start < start_date:
                week_start = start_date

            # 週の終了（日曜日）
            week_end = week_start + timedelta(days=6)

            # 月の終了日を超える場合は月の終了日に調整
            if week_end > end_date:
                week_end = end_date

            # 週のラベル（第一週、第二週など）
            week_label = f'第{week_number}週'

            weeks.append((week_start, week_end, week_label))

            # 次の週へ
            current_date = week_end + timedelta(days=1)
            week_number += 1

        return weeks

    @staticmethod
    def calculate_period_dates(period, offset):
        """期間とオフセットから日付範囲とラベルを計算

        Args:
            period: 'week', 'month', または 'preview'
            offset: オフセット値（整数）

        Returns:
            tuple: (start_date, end_date, period_label)
        """
        base_date = datetime.now().date()

        if period == 'week':
            # 週単位でオフセット
            base_date += timedelta(weeks=offset)
            start_date, end_date = AnalyticsService.get_week_range(base_date)
            period_label = f'{start_date.strftime("%Y年%m月%d日")} ~ {end_date.strftime("%m月%d日")}'
        elif period == 'preview':
            # プレビュー：月と同じ期間
            year = base_date.year
            month = base_date.month + offset
            while month < 1:
                month += 12
                year -= 1
            while month > 12:
                month -= 12
                year += 1
            base_date = base_date.replace(year=year, month=month)
            start_date, end_date = AnalyticsService.get_month_range(base_date)
            period_label = f'{start_date.strftime("%Y年%m月")}（プレビュー）'
        else:  # month
            # 月単位でオフセット
            year = base_date.year
            month = base_date.month + offset
            while month < 1:
                month += 12
                year -= 1
            while month > 12:
                month -= 12
                year += 1
            base_date = base_date.replace(year=year, month=month)
            start_date, end_date = AnalyticsService.get_month_range(base_date)
            period_label = f'{start_date.strftime("%Y年%m月")}'

        return start_date, end_date, period_label

    @staticmethod
    def get_graph_data_by_type(graph_type, store, start_date, end_date, genre=None, base_store=None, period='week', location=None):
        """グラフタイプに応じてデータを取得

        Args:
            graph_type: グラフの種類（'sales', 'customer_count', 'incident_by_location', 'incident_trend_by_location'）
            store: 店舗オブジェクト
            start_date: 開始日
            end_date: 終了日
            genre: ジャンル（incident_by_locationの場合のみ使用）
            base_store: 比較モードの自店舗（optional）
            period: 期間タイプ（'week' または 'month'）
            location: 場所コード（incident_trend_by_locationの場合のみ使用）

        Returns:
            dict: {title: str, chart_data: dict}

        Raises:
            ValueError: 不正なグラフタイプの場合
        """
        if graph_type == 'sales':
            chart_data = AnalyticsService.get_sales_data(store, start_date, end_date)
            title = '売上推移'
        elif graph_type == 'customer_count':
            chart_data = AnalyticsService.get_customer_count_data(store, start_date, end_date)
            title = '客数推移'
        elif graph_type == 'incident_by_location':
            chart_data = AnalyticsService.get_incident_by_location_data(store, start_date, end_date, genre, base_store, period)
            # ジャンル名のマッピング
            genre_labels = {
                'claim': 'クレーム',
                'praise': '賞賛',
                'accident': '事故',
                'report': '報告',
                'other': 'その他',
            }
            genre_label = genre_labels.get(genre, 'ネガティブジャンル') if genre else 'ネガティブジャンル'
            title = f'場所別できごと（{genre_label}）'
        elif graph_type == 'incident_trend_by_location':
            if not location:
                raise ValueError('場所が指定されていません')
            
            # ▼ 引数に base_store を追加
            chart_data = AnalyticsService.get_incident_trend_by_location(
                store, start_date, end_date, location, genre, period, base_store
            )
            # 場所名のマッピング
            location_labels = {
                'kitchen': 'キッチン',
                'hall': 'ホール',
                'cashier': 'レジ',
                'toilet': 'トイレ',
                'other': 'その他',
                'all': '全場所',
            }
            location_label = location_labels.get(location, location)
            # ジャンル名のマッピング
            genre_labels = {
                'claim': 'クレーム',
                'praise': '賞賛',
                'accident': '事故',
                'report': '報告',
                'other': 'その他',
            }
            genre_label = genre_labels.get(genre, 'ﾈｶﾞﾃｨﾌﾞｼﾞｬﾝﾙ') if genre else 'ﾈｶﾞﾃｨﾌﾞｼﾞｬﾝﾙ'
            title = f'{location_label}での出来事数推移({genre_label})'
        else:
            raise ValueError(f'不正なグラフタイプです: {graph_type}')

        return {
            'title': title,
            'chart_data': chart_data,
        }

    @staticmethod
    def get_monthly_goal_data(store, year=None, month=None):
        """月次目標データを取得

        Args:
            store: 店舗オブジェクト
            year: 年（Noneの場合は現在の年）
            month: 月（Noneの場合は現在の月）

        Returns:
            dict: 月次目標データ
        """
        today = datetime.now().date()
        year = year or today.year
        month = month or today.month

        try:
            goal = MonthlyGoal.objects.get(store=store, year=year, month=month)
            return {
                'year': goal.year,
                'month': goal.month,
                'goal_text': goal.goal_text,
                'achievement_rate': goal.achievement_rate,
                'achievement_text': goal.achievement_text,
            }
        except MonthlyGoal.DoesNotExist:
            return {
                'year': year,
                'month': month,
                'goal_text': '目標が設定されていません',
                'achievement_rate': 0,
                'achievement_text': '',
            }

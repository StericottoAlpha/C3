# Analytics Tests

分析機能のテストスイート

## テストファイル

### test_services.py
`AnalyticsService`クラスの単体テスト

**テストケース:**
- `test_get_sales_data`: 売上データ取得の検証
  - 7日分のデータが正しく取得できる
  - 期待値: [100000, 110000, 120000, 130000, 140000, 150000, 160000]
  
- `test_get_customer_count_data`: 客数データ取得の検証
  - 期待値: [50, 55, 60, 65, 70, 75, 80]
  
- `test_get_incident_count_data`: インシデント数データ取得の検証
  - 期待値: [1, 2, 1, 2, 1, 2, 1] (奇数日は2件、偶数日は1件)
  
- `test_get_week_range`: 週範囲の計算検証
  - 月曜日から日曜日の7日間を正しく計算

### test_views.py
グラフデータAPIのエンドツーエンドテスト

**テストケース:**
- `test_sales_graph_weekly`: 売上グラフAPIの検証
  - APIレスポンスのステータスコード
  - タイトルが「売上推移」
  - 7日分のデータが返される
  - データ値が正しい
  
- `test_customer_count_graph_weekly`: 客数グラフAPIの検証
  
- `test_incident_count_graph_weekly`: インシデント数グラフAPIの検証

## テストデータ

テストでは以下のパターンでデータを作成します：

### StoreDailyPerformance (売上・客数)
- 今週の月曜日から日曜日まで7日分
- 売上: `100000 + (i * 10000)` (i=0〜6)
- 客数: `50 + (i * 5)` (i=0〜6)

### DailyReport (インシデント)
- 偶数日(i=0,2,4,6): 1件
- 奇数日(i=1,3,5): 2件

## 実行方法

```bash
# 全テスト実行
python3 manage.py test analytics.tests

# サービステストのみ
python3 manage.py test analytics.tests.test_services

# APIテストのみ
python3 manage.py test analytics.tests.test_views

# 詳細出力
python3 manage.py test analytics.tests -v 2
```

## テスト結果の期待値

全7テストが成功することを期待:
- test_services.py: 4テスト
- test_views.py: 3テスト

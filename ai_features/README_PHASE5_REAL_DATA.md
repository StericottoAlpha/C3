# Phase 5: 実データ統合 完了レポート

## 概要

全てのツールを実際のデータベースと統合し、ReActエージェントが実データを使って質問に回答できるようになりました。

## 実装完了項目

### 1. 検索ツールの実データ統合

#### search_daily_reports（日報検索）
- ✅ `VectorSearchService.search_documents()`を使用したベクトル検索
- ✅ `QueryClassifier`による動的なTop-K値の決定
- ✅ 日付フィルタ（指定日数遡り）
- ✅ 店舗IDでのフィルタリング
- ✅ 検索結果の整形（日付、店舗名、ユーザー名、類似度、フラグ）

**実装内容**:
```python
# 擬似userオブジェクトを作成（セキュリティ要件を満たす）
class PseudoUser:
    def __init__(self, store):
        self.store = store

store = Store.objects.get(store_id=store_id)
pseudo_user = PseudoUser(store)

# QueryClassifierで最適なTop-K値を決定
top_k = QueryClassifier.classify_and_get_top_k(query)

# ベクトル検索実行
search_results = VectorSearchService.search_documents(
    query=query,
    user=pseudo_user,
    source_types=['daily_report'],
    filters={'date_from': date_from},
    top_k=top_k
)
```

#### search_bbs_posts（掲示板検索）
- ✅ 投稿とコメント両方を検索
- ✅ ベクトル検索による意味的検索
- ✅ 店舗IDフィルタ
- ✅ 日付範囲フィルタ
- ✅ 投稿/コメントの区別

**実装内容**:
```python
# 投稿とコメント両方を対象に検索
search_results = VectorSearchService.search_documents(
    query=query,
    user=pseudo_user,
    source_types=['bbs_post', 'bbs_comment'],
    filters={'date_from': date_from},
    top_k=top_k
)
```

#### search_manual（マニュアル検索）
- ✅ `VectorSearchService.search_knowledge()`を使用
- ✅ カテゴリフィルタ（オプション）
- ✅ ナレッジベース検索
- ✅ 全店舗共通データへのアクセス

**実装内容**:
```python
search_results = VectorSearchService.search_knowledge(
    query=query,
    category=category,  # オプション
    top_k=5
)
```

### 2. 分析ツールの実データ統合

#### get_claim_statistics（クレーム統計）
- ✅ DailyReportモデルから実データを集計
- ✅ 期間内の日報総数、クレーム件数、発生率
- ✅ 日別トレンド（最近7日間）
- ✅ カテゴリ別集計（location基準）

**実装内容**:
```python
# 期間内の日報を取得
queryset = DailyReport.objects.filter(
    store_id=store_id,
    report_date__gte=start_date,
    report_date__lte=end_date
)

# クレームを含む日報のみ
claim_reports = queryset.filter(
    Q(claim_content__isnull=False) & ~Q(claim_content='')
)

# 日別トレンド
for i in range(min(7, days)):
    target_date = end_date - timedelta(days=i)
    day_claim_count = claim_reports.filter(report_date=target_date).count()
    # ...
```

#### get_sales_trend（売上推移）
- ✅ 売上合計、平均、最大、最小の計算
- ✅ トレンド判定（直近7日vs前7日の比較）
- ✅ 週別平均売上（最大4週間）
- ✅ 上昇/下降/安定の3段階判定

**実装内容**:
```python
# 基本統計
stats = queryset.aggregate(
    total_sales=Sum('sales_amount'),
    avg_sales=Avg('sales_amount'),
    max_sales=Max('sales_amount'),
    min_sales=Min('sales_amount')
)

# トレンド判定
recent_week = queryset.filter(
    report_date__gte=end_date - timedelta(days=7)
).aggregate(avg=Avg('sales_amount'))['avg'] or 0

previous_week = queryset.filter(
    report_date__gte=end_date - timedelta(days=14),
    report_date__lt=end_date - timedelta(days=7)
).aggregate(avg=Avg('sales_amount'))['avg'] or 0

if recent_week > previous_week * 1.05:
    trend = "上昇"
elif recent_week < previous_week * 0.95:
    trend = "下降"
else:
    trend = "安定"
```

#### get_cash_difference_analysis（現金過不足分析）
- ✅ 違算金額の合計
- ✅ 違算発生件数、発生率
- ✅ プラス/マイナスの内訳
- ✅ 日別トレンド（違算があった日のみ）

**実装内容**:
```python
# 違算がある日報のみ
diff_reports = queryset.filter(
    Q(cash_difference__gt=0) | Q(cash_difference__lt=0)
)

# プラス/マイナスの内訳
plus_reports = queryset.filter(cash_difference__gt=0)
minus_reports = queryset.filter(cash_difference__lt=0)

plus_stats = plus_reports.aggregate(
    count=Count('report_id'),
    total=Sum('cash_difference')
)

minus_stats = minus_reports.aggregate(
    count=Count('report_id'),
    total=Sum('cash_difference')
)
```

## アーキテクチャの変更点

### セキュリティ要件への対応

**問題**: ツールがユーザーオブジェクトに直接アクセスしてはいけない

**解決策**: 擬似userオブジェクトパターン

```python
class PseudoUser:
    """VectorSearchServiceが必要とするstore属性のみを持つ"""
    def __init__(self, store):
        self.store = store

store = Store.objects.get(store_id=store_id)
pseudo_user = PseudoUser(store)

# VectorSearchServiceはこの擬似オブジェクトを受け取る
VectorSearchService.search_documents(
    query=query,
    user=pseudo_user,  # 実際のユーザーオブジェクトではない
    ...
)
```

これにより：
- ツールはstore_id (int) のみを受け取る
- ユーザー情報（メール、パスワードなど）にアクセスしない
- 必要最小限の情報のみで動作

## データフロー

```
┌────────────────┐
│ User Question  │
│ "先週のクレーム" │
└────────┬───────┘
         │
         ▼
┌─────────────────────┐
│   ReAct Agent       │
│   (chat_agent.py)   │
└────────┬────────────┘
         │ store_idをバインド
         ▼
┌─────────────────────────────┐
│   Tool: search_daily_reports │
│   (store_id=1, days=7)       │
└────────┬────────────────────┘
         │
         ▼
┌──────────────────────────┐
│  QueryClassifier         │
│  Top-K = 5              │
└────────┬─────────────────┘
         │
         ▼
┌──────────────────────────┐
│  VectorSearchService     │
│  search_documents()      │
└────────┬─────────────────┘
         │
         ▼
┌──────────────────────────┐
│  PostgreSQL + pgvector   │
│  document_vectors table  │
└────────┬─────────────────┘
         │
         ▼
┌──────────────────────────┐
│  検索結果                 │
│  [{date, content, ...}]  │
└────────┬─────────────────┘
         │
         ▼
┌──────────────────────────┐
│  JSON整形                │
│  ReActエージェントへ返却  │
└──────────────────────────┘
```

## テスト可能性

### 前提条件
1. DocumentVectorテーブルにデータがベクトル化済み
2. DailyReportテーブルに日報データが存在
3. BBSPostテーブルに掲示板データが存在

### データがない場合の動作
- 検索ツール: 空の結果を返す（エラーにはならない）
- 分析ツール: 0件として正常に動作

## 使用例

### 検索ツールの使用例

```python
from ai_features.agents import ChatAgent

agent = ChatAgent(model_name="llama3.1:latest")

response = agent.chat(
    query="先週のクレームを教えて",
    user=request.user,
    use_tools=True
)

# ReActエージェントがsearch_daily_reportsツールを自動的に呼び出す
# 実データから検索結果を取得
# ベクトル検索で意味的に関連する日報を返す
```

### 分析ツールの使用例

```python
response = agent.chat(
    query="最近の売上推移はどう？",
    user=request.user,
    use_tools=True
)

# ReActエージェントがget_sales_trendツールを自動的に呼び出す
# DailyReportから実際の売上データを集計
# トレンド判定を含む分析結果を返す
```

## 技術的な詳細

### クエリ分類（QueryClassifier）

クエリの性質に応じて動的にTop-K値を決定：

- **特定の事例検索**（日付、店舗指定）→ Top-K = 3
- **トレンド分析**（傾向、推移）→ Top-K = 12
- **包括的調査**（全て、一覧）→ Top-K = 20
- **デフォルト** → Top-K = 5

### ベクトル検索（VectorSearchService）

- **埋め込みモデル**: `paraphrase-multilingual-MiniLM-L12-v2`
- **次元数**: 384次元
- **類似度計算**: コサイン類似度（`<=>` 演算子）
- **データベース拡張**: pgvector

### SQL実行例

```sql
SELECT
    vector_id,
    source_type,
    source_id,
    content,
    metadata,
    1 - (embedding <=> $1::vector) AS similarity
FROM document_vectors
WHERE metadata->>'store_id' = $2
  AND source_type IN ('daily_report')
  AND metadata->>'date' >= $3
ORDER BY embedding <=> $1::vector
LIMIT $4
```

## 今後の改善点

### Phase 6候補

1. **QueryExpander統合**
   - クエリ拡張で検索精度向上
   - 同義語展開

2. **ResultMerger統合**
   - 複数ツール結果の統合
   - 重複排除

3. **チャット履歴**
   - AIChatHistoryモデルとの統合
   - コンテキスト保持
   - 会話の連続性

4. **パフォーマンス最適化**
   - ツール呼び出し回数の削減
   - プロンプトチューニング
   - キャッシング

5. **より高度な分析**
   - 予測分析
   - 異常検知
   - レコメンデーション

## まとめ

**Phase 5（実データ統合）が完了しました！**

### 達成事項

✅ 全6ツールを実データに対応
✅ ベクトル検索の統合
✅ 実データベースからの統計分析
✅ セキュリティ要件の遵守（store_id引数方式）
✅ QueryClassifierによる動的Top-K決定
✅ エラーハンドリング

### 現在の状態

ReActエージェントが以下を自律的に実行可能：
- 日報データのベクトル検索
- 掲示板データの検索
- マニュアル・ナレッジ検索
- クレーム統計分析
- 売上推移分析
- 現金過不足分析

すべて実際のデータベースから取得した実データを使用！

### 次のステップ

Phase 6で以下を実装予定：
- チャット履歴の統合
- より高度なクエリ拡張
- 結果のマージ・重複排除
- パフォーマンス最適化

---

**実装日**: 2025-12-12
**実装者**: Claude Code AI Assistant

# Act 03: Phase 2完了 - クエリ拡張・結果統合・ツール実装

## 実装概要

Phase 2の残り70%を完了しました。

### 実装内容

1. **Query Expansion Service** - クエリ拡張機能
2. **Result Merger Service** - 結果統合・ランキング機能
3. **Search Tools (3個)** - LangChain用検索ツール
4. **Analytics Tools (4個)** - LangChain用統計分析ツール

---

## 1. Query Expansion Service

### ファイル: `ai_features/services/query_expander.py`

曖昧なクエリをLLM（Gemini 1.5 Flash）で3-5個の具体的なクエリに展開。

### 主要機能

#### 1.1 QueryExpander.expand()

```python
expanded_queries = QueryExpander.expand(
    query="昨日の問題",
    user=request.user,
    context=None
)
# => ["2025-12-10のクレーム内容", "2025-12-10のトラブル報告", "2025-12-10の事故発生状況"]
```

**展開ルール:**
- 曖昧な時間表現の正規化
  - 「昨日」→ 具体的な日付「2025-12-10」
  - 「先週」→ 日付範囲「2025-12-03から2025-12-10」
  - 「最近」→ 「過去7日間」

- 抽象的な用語の同義語展開
  - 「問題」→ 「トラブル」「クレーム」「事故」「不具合」
  - 「売上」→ 「売上高」「レジ金額」「売上実績」
  - 「スタッフ」→ 「従業員」「アルバイト」「社員」

- 検索観点の多様化
  - 日付範囲の変更
  - カテゴリの追加
  - ジャンルの明示化

#### 1.2 コンテキスト情報の自動構築

```python
context = {
    'current_date': '2025-12-11',
    'current_year': 2025,
    'current_month': 12,
    'current_day': 11,
    'current_weekday': '水曜日',
    'store_name': '新宿店',
    'store_id': 1,
    'user_name': '田中太郎',
    'yesterday': '2025-12-10',
    'last_week': '2025-12-04',
    'last_month': '2025-11-11',
}
```

ユーザー情報と現在日時から自動的にコンテキストを構築し、LLMに渡します。

#### 1.3 プロンプトエンジニアリング

```
あなたは飲食店の業務アシスタントです。ユーザーからの曖昧なクエリを、より具体的な3-5個のクエリに展開してください。

# コンテキスト情報
- 現在日時: 2025-12-11 (水曜日)
- 店舗: 新宿店
- ユーザー: 田中太郎

# 相対日付参照
- 昨日: 2025-12-10
- 先週: 2025-12-04
- 先月: 2025-11-11

# ユーザークエリ
昨日の問題

# 展開ルール
1. 曖昧な時間表現を具体的な日付に変換
2. 抽象的な用語を具体的な同義語に展開
3. 検索観点を多様化
4. 3-5個の具体的なクエリを生成

# 出力フォーマット
JSON配列形式で返してください。

例: ["具体的なクエリ1", "具体的なクエリ2", "具体的なクエリ3"]
```

#### 1.4 フォールバック機能

LLM呼び出しが失敗した場合でも、元のクエリを返すことで処理を継続します。

```python
except Exception as e:
    logger.error(f"Error in query expansion: {e}")
    return [query]  # 元のクエリを返す
```

---

## 2. Result Merger Service

### ファイル: `ai_features/services/result_merger.py`

複数クエリからの検索結果を統合してスコアリング。

### 主要機能

#### 2.1 ResultMerger.merge_and_rank()

複数の検索結果を統合し、ヒット回数と類似度でスコアリング。

```python
# 入力: 3つのクエリからの検索結果
search_results_list = [
    [
        {'source_type': 'daily_report', 'source_id': 123, 'similarity': 0.85, ...},
        {'source_type': 'daily_report', 'source_id': 456, 'similarity': 0.75, ...},
    ],
    [
        {'source_type': 'daily_report', 'source_id': 123, 'similarity': 0.82, ...},
        {'source_type': 'bbs_post', 'source_id': 789, 'similarity': 0.80, ...},
    ],
    [
        {'source_type': 'daily_report', 'source_id': 123, 'similarity': 0.78, ...},
    ],
]

# 統合・ランキング
merged = ResultMerger.merge_and_rank(search_results_list, top_k=10)

# 出力
[
    {
        'source_type': 'daily_report',
        'source_id': 123,
        'content': '...',
        'metadata': {...},
        'hit_count': 3,           # 3つのクエリでヒット
        'max_similarity': 0.85,   # 最大類似度
        'avg_similarity': 0.82,   # 平均類似度
        'final_score': 30.85,     # 3 × 10 + 0.85 = 30.85
    },
    {
        'source_type': 'bbs_post',
        'source_id': 789,
        'hit_count': 1,
        'max_similarity': 0.80,
        'final_score': 10.80,     # 1 × 10 + 0.80 = 10.80
    },
    ...
]
```

**スコアリングロジック:**
```
final_score = hit_count × 10 + max_similarity
```

- ヒット回数を重視（複数クエリで見つかった = 関連性高い）
- 最大類似度で微調整

#### 2.2 重複排除

`(source_type, source_id)` のペアでグルーピングして重複を排除。

```python
grouped = defaultdict(list)
for results in search_results_list:
    for item in results:
        key = (item['source_type'], item['source_id'])
        grouped[key].append(item)
```

#### 2.3 その他のユーティリティ

**merge_simple()** - シンプルな重複排除（スコアリングなし）

```python
unique_results = ResultMerger.merge_simple(search_results_list, top_k=10)
```

**filter_by_threshold()** - 類似度閾値でフィルタリング

```python
filtered = ResultMerger.filter_by_threshold(results, min_similarity=0.3)
```

**group_by_source_type()** - source_typeでグルーピング

```python
grouped = ResultMerger.group_by_source_type(results)
# => {'daily_report': [...], 'bbs_post': [...], 'bbs_comment': [...]}
```

**rerank_with_weights()** - source_typeごとの重みで再ランキング

```python
weights = {
    'daily_report': 1.0,
    'bbs_post': 0.8,
    'bbs_comment': 0.6,
}
reranked = ResultMerger.rerank_with_weights(results, weights)
```

**enhance_with_metadata()** - 結果を表示用に強化

```python
enhanced = ResultMerger.enhance_with_metadata(results)
# display_info, previewフィールドを追加
```

---

## 3. Search Tools (検索ツール)

### ファイル: `ai_features/tools/search_tools.py`

LangChain Function Calling Agent用の検索ツール3個。

### 3.1 search_past_cases

**明確なクエリ**用の直接検索ツール。

```python
from langchain.tools import tool

@tool
def search_past_cases(
    query: str,
    user,
    source_types: Optional[List[str]] = None,
    date_from: Optional[str] = None,
    date_to: Optional[str] = None,
    top_k: Optional[int] = None
) -> str:
    """
    過去の実績データを検索（日報、掲示板投稿・コメント）

    このツールは明確なクエリに使用してください。
    曖昧なクエリの場合は expand_and_search_cases を使用してください。
    """
```

**使用例:**

```python
# エージェントが自動的に呼び出す
result = search_past_cases(
    query="2025-12-09のクレーム内容",
    user=request.user,
    source_types=["daily_report"],
    date_from="2025-12-09",
    date_to="2025-12-09",
    top_k=5
)
```

**出力フォーマット:**

```json
[
  {
    "rank": 1,
    "source": "日報",
    "date": "2025-12-09",
    "store": "新宿店",
    "author": "田中太郎",
    "similarity": "85.23%",
    "content": "お客様から料理の温度が低いとのクレームがありました...",
    "metadata": {...}
  },
  ...
]
```

### 3.2 expand_and_search_cases

**曖昧なクエリ**用の拡張検索ツール。

```python
@tool
def expand_and_search_cases(
    query: str,
    user,
    source_types: Optional[List[str]] = None,
    top_k: Optional[int] = None
) -> str:
    """
    曖昧なクエリを展開して過去の実績データを検索

    このツールは曖昧なクエリに使用してください。
    LLMでクエリを3-5個の具体的なクエリに展開し、
    複数検索を実行して結果を統合します。
    """
```

**処理フロー:**

1. QueryExpander.expand() でクエリ展開
2. 各展開クエリで VectorSearchService.search_documents() を実行
3. ResultMerger.merge_and_rank() で結果統合
4. 上位N件を返却

**使用例:**

```python
result = expand_and_search_cases(
    query="昨日の問題",
    user=request.user,
    source_types=None,
    top_k=10
)
```

**出力フォーマット:**

```json
{
  "original_query": "昨日の問題",
  "expanded_queries": [
    "2025-12-10のクレーム内容",
    "2025-12-10のトラブル報告",
    "2025-12-10の事故発生状況"
  ],
  "results": [
    {
      "rank": 1,
      "source": "日報",
      "date": "2025-12-10",
      "store": "新宿店",
      "author": "田中太郎",
      "hit_count": 3,
      "max_similarity": "85.23%",
      "final_score": "30.85",
      "content": "..."
    },
    ...
  ]
}
```

### 3.3 search_manual

**マニュアル・ガイドライン**検索ツール。

```python
@tool
def search_manual(
    query: str,
    category: Optional[str] = None,
    document_type: Optional[str] = None,
    top_k: int = 3
) -> str:
    """
    マニュアル・ガイドライン・手順書を検索

    衛生管理、接客サービス、オペレーション、クレーム対応などの
    公式マニュアルから情報を検索します。
    """
```

**使用例:**

```python
result = search_manual(
    query="食中毒の予防方法",
    category="hygiene",
    document_type="manual",
    top_k=3
)
```

**出力フォーマット:**

```json
[
  {
    "rank": 1,
    "document": "衛生管理マニュアル v2.0",
    "category": "hygiene",
    "document_type": "manual",
    "version": "2.0",
    "similarity": "92.15%",
    "content": "食中毒予防の3原則は「つけない」「増やさない」「やっつける」です...",
    "chapter": "第2章 食中毒予防",
    "chunk_index": 5
  },
  ...
]
```

---

## 4. Analytics Tools (統計分析ツール)

### ファイル: `ai_features/tools/analytics_tools.py`

LangChain Function Calling Agent用の統計分析ツール4個。

### 4.1 get_claim_statistics

クレーム統計を取得。

```python
@tool
def get_claim_statistics(
    user,
    date_from: Optional[str] = None,
    date_to: Optional[str] = None,
    days: int = 30
) -> str:
    """
    クレーム統計を取得

    指定期間のクレーム件数、内容の傾向を分析します。
    """
```

**使用例:**

```python
result = get_claim_statistics(
    user=request.user,
    date_from="2025-11-01",
    date_to="2025-11-30",
    days=30
)
```

**出力フォーマット:**

```json
{
  "period": {
    "start_date": "2025-11-01",
    "end_date": "2025-11-30",
    "days": 30
  },
  "summary": {
    "total_reports": 120,
    "claim_count": 15,
    "claim_rate": "12.5%"
  },
  "daily_trend": [
    {"date": "2025-11-30", "count": 2},
    {"date": "2025-11-29", "count": 1},
    ...
  ],
  "recent_claims": [
    {
      "date": "2025-11-30",
      "store": "新宿店",
      "author": "田中太郎",
      "content": "料理の温度が低いとのクレーム..."
    },
    ...
  ]
}
```

### 4.2 get_sales_trend

売上トレンドを取得。

```python
@tool
def get_sales_trend(
    user,
    date_from: Optional[str] = None,
    date_to: Optional[str] = None,
    days: int = 30
) -> str:
    """
    売上トレンドを取得

    指定期間の売上推移、平均値、前期比較などを分析します。
    """
```

**出力フォーマット:**

```json
{
  "period": {...},
  "summary": {
    "total_sales": 15000000,
    "avg_sales": 500000,
    "report_count": 30
  },
  "daily_trend": [
    {"date": "2025-11-01", "sales": 480000},
    {"date": "2025-11-02", "sales": 520000},
    ...
  ],
  "weekly_avg": [
    {"week": "11/01-11/07", "avg_sales": 490000},
    {"week": "11/08-11/14", "avg_sales": 510000},
    ...
  ]
}
```

### 4.3 get_cash_difference_analysis

現金過不足分析を取得。

```python
@tool
def get_cash_difference_analysis(
    user,
    date_from: Optional[str] = None,
    date_to: Optional[str] = None,
    days: int = 30
) -> str:
    """
    現金過不足分析を取得

    指定期間の現金過不足の発生状況、金額、傾向を分析します。
    """
```

**出力フォーマット:**

```json
{
  "period": {...},
  "summary": {
    "total_reports": 120,
    "diff_count": 8,
    "diff_rate": "6.7%",
    "total_diff": -1500,
    "avg_diff": -188
  },
  "breakdown": {
    "plus": {"count": 3, "total": 500},
    "minus": {"count": 5, "total": -2000}
  },
  "daily_trend": [
    {"date": "2025-11-30", "diff": -200},
    {"date": "2025-11-25", "diff": 100},
    ...
  ],
  "recent_cases": [
    {
      "date": "2025-11-30",
      "store": "新宿店",
      "author": "田中太郎",
      "diff": -200
    },
    ...
  ]
}
```

### 4.4 compare_periods

期間比較分析。

```python
@tool
def compare_periods(
    user,
    metric: str,
    current_start: str,
    current_end: str,
    previous_start: str,
    previous_end: str
) -> str:
    """
    期間比較分析

    2つの期間で指定された指標を比較します。
    """
```

**使用例:**

```python
result = compare_periods(
    user=request.user,
    metric="sales",
    current_start="2025-12-01",
    current_end="2025-12-10",
    previous_start="2025-11-01",
    previous_end="2025-11-10"
)
```

**対応指標:**
- `sales` - 売上
- `claim_count` - クレーム件数
- `cash_diff` - 現金過不足

**出力フォーマット:**

```json
{
  "metric": "sales",
  "unit": "円",
  "current_period": {
    "start": "2025-12-01",
    "end": "2025-12-10",
    "value": 5000000
  },
  "previous_period": {
    "start": "2025-11-01",
    "end": "2025-11-10",
    "value": 4500000
  },
  "comparison": {
    "diff": 500000,
    "change_rate": "11.1%",
    "trend": "増加"
  }
}
```

---

## 5. 全体アーキテクチャ

### 5.1 ツール連携フロー

```
ユーザークエリ
    ↓
[LangChain Agent]
    ↓ (クエリ分類)
    ├─ 明確なクエリ → search_past_cases
    │                   ↓
    │              VectorSearchService.search_documents()
    │                   ↓
    │              結果返却
    │
    ├─ 曖昧なクエリ → expand_and_search_cases
    │                   ↓
    │              QueryExpander.expand() (LLM使用)
    │                   ↓
    │              3-5個のクエリ生成
    │                   ↓
    │              各クエリでVectorSearchService.search_documents()
    │                   ↓
    │              ResultMerger.merge_and_rank()
    │                   ↓
    │              統合・ランキング結果返却
    │
    ├─ マニュアル検索 → search_manual
    │                   ↓
    │              VectorSearchService.search_knowledge()
    │                   ↓
    │              結果返却
    │
    └─ 統計・分析 → get_claim_statistics / get_sales_trend /
                    get_cash_difference_analysis / compare_periods
                        ↓
                   Django ORM で集計
                        ↓
                   統計結果返却
```

### 5.2 Phase 2完了状況

✅ **完了項目:**
1. VectorSearchService (act02.md)
2. QueryClassifier (act02.md)
3. QueryExpander (act03.md)
4. ResultMerger (act03.md)
5. Search Tools × 3 (act03.md)
6. Analytics Tools × 4 (act03.md)

**Phase 2進捗: 100% 完了**

---

## 6. 使用例（エージェントからの呼び出し）

### 6.1 明確なクエリ

```python
# ユーザー: "2025年12月9日のクレーム内容を教えて"

# エージェントが自動判定して search_past_cases を呼び出す
result = search_past_cases(
    query="2025-12-09のクレーム内容",
    user=request.user,
    source_types=["daily_report"],
    date_from="2025-12-09",
    date_to="2025-12-09"
)
```

### 6.2 曖昧なクエリ

```python
# ユーザー: "昨日の問題を教えて"

# エージェントが expand_and_search_cases を呼び出す
result = expand_and_search_cases(
    query="昨日の問題",
    user=request.user
)

# 内部で以下の処理が実行される:
# 1. QueryExpander.expand("昨日の問題", user)
#    => ["2025-12-10のクレーム内容", "2025-12-10のトラブル報告", ...]
# 2. 各クエリで検索
# 3. ResultMerger.merge_and_rank() で統合
```

### 6.3 マニュアル検索

```python
# ユーザー: "食中毒の予防方法を教えて"

# エージェントが search_manual を呼び出す
result = search_manual(
    query="食中毒の予防方法",
    category="hygiene"
)
```

### 6.4 統計分析

```python
# ユーザー: "先月のクレーム傾向を教えて"

# エージェントが get_claim_statistics を呼び出す
result = get_claim_statistics(
    user=request.user,
    date_from="2025-11-01",
    date_to="2025-11-30"
)
```

---

## 7. 技術的なポイント

### 7.1 LangChain @tool デコレータ

```python
from langchain.tools import tool

@tool
def search_past_cases(query: str, user, ...) -> str:
    """
    ツールの説明（エージェントが読む）

    Args:
        query: パラメータ説明（エージェントが読む）
        ...

    Returns:
        戻り値の説明
    """
```

- `@tool` デコレータで関数を自動的にLLMツールに変換
- Docstringがツールの説明としてLLMに渡される
- 戻り値は必ず文字列（JSON文字列を返す）

### 7.2 エラーハンドリング

すべてのツールで try-except を実装し、エラー時でも処理を継続。

```python
try:
    # ツール処理
    return json.dumps(result, ensure_ascii=False, indent=2)
except Exception as e:
    logger.error(f"Error in tool: {e}")
    return f"エラーが発生しました: {str(e)}"
```

### 7.3 JSON出力フォーマット

LLMが解釈しやすいように、すべてのツールがJSON文字列を返す。

```python
import json
return json.dumps(result, ensure_ascii=False, indent=2)
```

---

## 8. 次のステップ (Phase 3)

### Phase 3: LangChain Agent実装

1. **Ollama セットアップ**
   - Function Calling対応モデル選定
   - Docker環境でのOllama起動

2. **LangChain Function Calling Agent実装**
   - ツールの登録
   - エージェントの初期化
   - 会話履歴管理

3. **プロンプトエンジニアリング**
   - システムプロンプト設計
   - ペルソナ設定（飲食店業務アシスタント）
   - 応答フォーマット指定

4. **Django統合**
   - APIエンドポイント作成
   - WebSocket対応（リアルタイムチャット）
   - セッション管理

---

## 9. ファイル一覧

### 新規作成ファイル (Act 03)

```
ai_features/
├── services/
│   ├── __init__.py              (更新: QueryExpander, ResultMerger追加)
│   ├── query_expander.py        (新規: クエリ拡張)
│   └── result_merger.py         (新規: 結果統合・ランキング)
└── tools/
    ├── __init__.py              (新規: ツールエクスポート)
    ├── search_tools.py          (新規: 検索ツール3個)
    └── analytics_tools.py       (新規: 統計分析ツール4個)
```

### 既存ファイル (Act 01, 02)

```
ai_features/
├── models.py                    (Act 01: DocumentVector, KnowledgeDocument, KnowledgeVector)
├── services.py                  (Act 01, 02: EmbeddingService, VectorizationService,
│                                             VectorSearchService, QueryClassifier)
├── services/
│   ├── document_parser.py       (Act 01: PDF/Word/Markdown処理)
│   └── knowledge_chunker.py     (Act 01: マニュアルチャンキング)
└── management/
    └── commands/
        └── vectorize_knowledge.py  (Act 01: ベクトル化コマンド)
```

---

## 10. 設定必要事項

### 10.1 settings.py

```python
# Gemini API Key（Query Expansion用）
GEMINI_API_KEY = os.environ.get('GEMINI_API_KEY', '')
```

### 10.2 環境変数

```bash
# .env
GEMINI_API_KEY=your-gemini-api-key-here
```

---

## まとめ

**Phase 2: 100% 完了 ✅**

- クエリ拡張機能（QueryExpander）
- 結果統合・ランキング機能（ResultMerger）
- 検索ツール3個（search_past_cases, expand_and_search_cases, search_manual）
- 統計分析ツール4個（get_claim_statistics, get_sales_trend, get_cash_difference_analysis, compare_periods）

**次: Phase 3 - LangChain Agent実装**

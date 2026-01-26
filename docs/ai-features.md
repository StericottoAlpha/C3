# AI機能詳細

本ドキュメントでは、C3 ステリコットαのAIチャット機能について詳細に説明します。

---

## 概要

AI機能は、店舗スタッフがPDCAサイクルを効率的に回すためのアシスタントです。日報や掲示板のデータを検索・分析し、売上やクレームなどの統計情報を提供します。

### 主な機能

- **データ検索**: 日報、掲示板、マニュアルからの情報検索
- **統計分析**: 売上トレンド、クレーム統計、違算金額分析
- **PDCA支援**: 目標達成に向けたアドバイス、改善提案
- **期間比較**: 先週・先月との比較分析

---

## 技術スタック

| コンポーネント | 技術 | 用途 |
|--------------|------|------|
| **LLM** | OpenAI GPT-4o-mini | 自然言語処理、回答生成 |
| **エージェント** | LangGraph ReAct Agent | ツール選択・実行の制御 |
| **ベクトルDB** | PostgreSQL + pgvector | セマンティック検索 |
| **ストリーミング** | FastAPI + Uvicorn | リアルタイム応答 |

---

## アーキテクチャ

```
ユーザー入力
    │
    ▼
┌──────────────────────┐
│     ChatAgent        │
│  (ReAct Agent)       │
│  - GPT-4o-mini       │
│  - Tool Selection    │
└──────────┬───────────┘
           │
           ▼
┌──────────────────────┐
│     Tool Execution   │
│  - Search Tools      │
│  - Analytics Tools   │
└──────────┬───────────┘
           │
           ▼
┌──────────────────────────────────────────┐
│              Data Sources                 │
│  ┌─────────────┐  ┌─────────────────────┐│
│  │   Vector    │  │    PostgreSQL       ││
│  │   Search    │  │  (Direct Query)     ││
│  └──────┬──────┘  └──────────┬──────────┘│
│         │                    │           │
│  pgvector検索          SQL集計クエリ     │
└──────────────────────────────────────────┘
           │
           ▼
回答生成（ストリーミング）
    │
    ▼
ユーザーに表示
```

---

## チャットエージェント

### ChatAgent クラス

**ファイル**: `ai_features/agents/chat_agent.py`

```python
class ChatAgent:
    def __init__(
        self,
        model_name: str = "gpt-4o-mini",
        temperature: float = 0.0,
        openai_api_key: Optional[str] = None,
    )
```

**主要メソッド**:

| メソッド | 説明 |
|---------|------|
| `chat()` | 非ストリーミングでチャット実行 |
| `chat_stream()` | ストリーミングでチャット実行（Generator） |

### 処理フロー

1. **コンテキスト構築**: ユーザー情報、店舗情報をシステムプロンプトに含める
2. **ツールバインド**: 店舗IDをクロージャでバインドしたツールを生成
3. **ReActループ**: ツール呼び出しと結果の処理を繰り返す
4. **回答生成**: 収集した情報を基に日本語で回答を生成

### システムプロンプト

エージェントには以下の指示が与えられます：

- **PDCA支援**: 目標設定、実行監視、結果分析、改善提案
- **必ずツールを使用**: データベースの情報のみを基に回答
- **日本語で回答**: 簡潔で箇条書きを活用

---

## 利用可能なツール

### 検索ツール（Search Tools）

**ファイル**: `ai_features/tools/search_tools.py`

#### search_daily_reports
日報を検索します（自店舗）。

```python
@tool
def search_daily_reports(query: str = "", store_id: int = 0, days: int = 60) -> str:
    """
    自店舗の日報データを検索します。

    Args:
        query: 検索クエリ（例: "先週のクレーム"）
        store_id: 店舗ID
        days: 検索対象日数
    """
```

**使用例**:
- 「先週のクレーム」 → `search_daily_reports(query="クレーム", days=7)`
- 「今月の事故」 → `search_daily_reports(query="事故", days=30)`

---

#### search_bbs_posts
掲示板投稿を検索します（全店舗）。

```python
@tool
def search_bbs_posts(query: str = "", days: int = 30) -> str:
    """
    全店舗の掲示板の投稿を検索し、各投稿のコメントも返します。
    """
```

**特徴**:
- 本部からのお知らせも含む
- コメント（議論の流れ）も取得
- ベストアンサーがあれば表示

---

#### search_bbs_by_keyword
掲示板をキーワードで直接検索します（DB検索）。

```python
@tool
def search_bbs_by_keyword(keyword: str, days: int = 60) -> str:
    """
    タイトル・内容に含まれるキーワードで確実に検索します。
    """
```

**使用例**:
- 「営業時間」「シフト」「お知らせ」などの具体的なキーワード検索

---

#### search_manual
マニュアル・ガイドラインを検索します。

```python
@tool
def search_manual(query: str = "", category: Optional[str] = None) -> str:
    """
    業務マニュアル・ガイドライン・手順書を検索します。
    """
```

**使用例**:
- 「クレーム対応手順」
- 「食中毒予防」

---

#### search_by_genre
ジャンル別に日報を検索します。

```python
@tool
def search_by_genre(query: str, store_id: int, genre: str, days: int = 60) -> str:
    """
    ジャンルで絞り込んで検索します。

    Args:
        genre: claim/praise/accident/report/other
    """
```

**ジャンル一覧**:
| 値 | 説明 |
|------|------|
| `claim` | クレーム |
| `praise` | 賞賛 |
| `accident` | 事故 |
| `report` | 報告 |
| `other` | その他 |

---

#### search_by_location
場所別に日報を検索します。

```python
@tool
def search_by_location(query: str, store_id: int, location: str, days: int = 60) -> str:
    """
    場所で絞り込んで検索します。

    Args:
        location: kitchen/hall/cashier/toilet/other
    """
```

**場所一覧**:
| 値 | 説明 |
|------|------|
| `kitchen` | キッチン |
| `hall` | ホール |
| `cashier` | レジ |
| `toilet` | トイレ |
| `other` | その他 |

---

### 統計・分析ツール（Analytics Tools）

**ファイル**: `ai_features/tools/analytics_tools.py`

#### get_claim_statistics
クレーム統計を取得します。

```python
@tool
def get_claim_statistics(store_id: int, days: int = 30) -> str:
    """
    クレーム件数、発生率、日別トレンド、場所別内訳を返します。
    """
```

**返却データ**:
- 総クレーム件数
- クレーム発生率
- 日別トレンド（直近7日）
- 場所別内訳

---

#### get_sales_trend
売上トレンドを取得します。

```python
@tool
def get_sales_trend(store_id: int, days: int = 30) -> str:
    """
    売上推移データを返します。
    """
```

**返却データ**:
- 合計売上
- 平均売上
- 日別売上（直近7日）
- 週次比較（先週との比較）
- 客単価

---

#### get_sales_by_date
特定日の売上を取得します。

```python
@tool
def get_sales_by_date(store_id: int, date: str) -> str:
    """
    指定した日の売上・客数・客単価を返します。

    Args:
        date: YYYY-MM-DD形式
    """
```

**使用例**:
- 「1/24の売上」 → `get_sales_by_date(date="2026-01-24")`

---

#### get_sales_by_date_range
期間指定で売上を取得します。

```python
@tool
def get_sales_by_date_range(store_id: int, start_date: str, end_date: str) -> str:
    """
    指定期間の売上・客数の集計と日別内訳を返します。
    """
```

**使用例**:
- 「1/20から1/24の売上」 → `get_sales_by_date_range(start_date="2026-01-20", end_date="2026-01-24")`

---

#### get_cash_difference_analysis
違算金額分析を取得します。

```python
@tool
def get_cash_difference_analysis(store_id: int, days: int = 30) -> str:
    """
    現金過不足の分析データを返します。
    """
```

**返却データ**:
- 合計違算金額
- 発生回数・発生率
- プラス/マイナス内訳
- 直近の違算発生日

---

#### get_report_statistics
日報統計を取得します。

```python
@tool
def get_report_statistics(store_id: int, days: int = 30) -> str:
    """
    日報の投稿統計を返します。
    """
```

**返却データ**:
- 総日報件数
- ジャンル別内訳
- 場所別内訳
- 日別投稿数

---

#### get_monthly_goal_status
月次目標状況を取得します。

```python
@tool
def get_monthly_goal_status(store_id: int) -> str:
    """
    今月の目標と達成率を返します。
    """
```

**返却データ**:
- 今月の目標テキスト
- 達成率
- 過去の目標履歴（最大5件）

---

### PDCA支援ツール

#### gather_topic_related_data
トピックに関連するデータを総合的に収集します。

```python
@tool
def gather_topic_related_data(topic: str, store_id: int, days: int = 30) -> str:
    """
    複数ソースから包括的なデータを収集します。
    """
```

**収集するデータ**:
1. 日報（キーワード検索）
2. 掲示板（キーワード検索 + コメント）
3. 関連統計（クレーム、売上、事故など）

**使用例**:
- 「クレームについてアドバイス」 → `gather_topic_related_data(topic="クレーム")`

---

#### compare_periods
期間比較を行います。

```python
@tool
def compare_periods(store_id: int, metric: str, period1_days: int = 7, period2_days: int = 14) -> str:
    """
    2期間の比較データを返します。

    Args:
        metric: sales/claims/accidents/reports/cash_difference
    """
```

**使用例**:
- 「先週と比べてクレームは増えた？」 → `compare_periods(metric="claims")`

**比較可能な指標**:
| metric | 説明 |
|--------|------|
| `sales` | 売上 |
| `claims` | クレーム件数 |
| `accidents` | 事故件数 |
| `reports` | 日報件数 |
| `cash_difference` | 違算金額 |

---

### 全店舗ツール

以下のツールは全店舗のデータを対象とします：

| ツール名 | 説明 |
|---------|------|
| `search_daily_reports_all_stores` | 全店舗の日報検索 |
| `search_bbs_posts_all_stores` | 全店舗の掲示板検索 |
| `search_by_genre_all_stores` | 全店舗のジャンル別検索 |
| `search_by_location_all_stores` | 全店舗の場所別検索 |
| `get_claim_statistics_all_stores` | 全店舗のクレーム統計 |
| `get_report_statistics_all_stores` | 全店舗の日報統計 |
| `gather_topic_related_data_all_stores` | 全店舗のトピック関連データ |

---

## ベクトル検索

### DocumentVector モデル

**テーブル**: `document_vectors`

| カラム | 説明 |
|--------|------|
| `source_type` | ソース種別（daily_report, bbs_post, etc.） |
| `source_id` | 元データのID |
| `content` | コンテンツテキスト |
| `metadata` | メタデータ（JSON） |
| `embedding` | 384次元ベクトル |

### KnowledgeVector モデル

**テーブル**: `knowledge_vectors`

| カラム | 説明 |
|--------|------|
| `document_type` | ドキュメント種別（manual, faq, etc.） |
| `title` | タイトル |
| `content` | コンテンツテキスト |
| `metadata` | メタデータ（JSON） |
| `embedding` | 384次元ベクトル |

### 検索サービス

**ファイル**: `ai_features/services/core_services.py`

```python
class VectorSearchService:
    @staticmethod
    def search_documents(
        query: str,
        store_id: Optional[int] = None,
        source_types: List[str] = None,
        filters: Dict = None,
        top_k: int = 5
    ) -> List[Dict]:
        """
        ベクトル検索を実行します。
        """
```

---

## ストリーミング処理

### 処理フロー

1. **メインサーバー**: リクエスト受信、認証確認
2. **ストリーミングサーバー**: チャット処理、SSE送信
3. **クライアント**: Server-Sent Eventsで受信

### イベント形式

```
data: {"type": "token", "content": "こんにちは"}
data: {"type": "token", "content": "！"}
data: {"type": "done"}
```

### 設定

| 環境変数 | 説明 |
|---------|------|
| `STREAM_API_URL` | ストリーミングサーバーのURL |
| `OPENAI_MODEL` | 使用するモデル名 |
| `MAX_CHAT_HISTORY` | 保持する履歴件数 |

---

## チャット履歴

### AIChatHistory モデル

**テーブル**: `ai_chat_history`

| カラム | 説明 |
|--------|------|
| `chat_id` | 主キー |
| `user` | ユーザーID |
| `role` | 役割（user/assistant） |
| `message` | メッセージ内容 |
| `created_at` | 作成日時 |

### 履歴管理

- **保持件数**: `MAX_CHAT_HISTORY`環境変数で設定（デフォルト: 14件）
- **クリア**: `/ai/api/chat/history/clear/`で全削除可能

---

## 使用例

### 質問例と期待される動作

| 質問 | 使用されるツール |
|------|-----------------|
| 「先週のクレーム件数は？」 | `get_claim_statistics(days=7)` |
| 「先週のクレームの内容」 | `search_by_genre(genre="claim", days=7)` |
| 「1/24の売上は？」 | `get_sales_by_date(date="2026-01-24")` |
| 「今月の目標達成状況」 | `get_monthly_goal_status()` |
| 「クレーム改善のアドバイス」 | `gather_topic_related_data(topic="クレーム")` |
| 「先週と比べて売上は？」 | `compare_periods(metric="sales")` |
| 「年末年始の営業時間」 | `search_bbs_by_keyword(keyword="営業時間")` |
| 「他店舗のクレーム対応事例」 | `search_daily_reports_all_stores(query="クレーム対応")` |

---

## トラブルシューティング

### 回答が返ってこない

1. OpenAI APIキーが正しく設定されているか確認
2. ストリーミングサーバーが起動しているか確認
3. ログでエラーを確認

### データが見つからない

1. 検索期間（days）が適切か確認
2. キーワードを変えて再検索
3. ベクトル検索ではなくキーワード検索（search_bbs_by_keyword）を試す

### 応答が遅い

1. 複数ツール実行時は時間がかかる
2. ネットワーク状況を確認
3. ストリーミングサーバーのログを確認

---

## 関連ドキュメント

- [システムアーキテクチャ](./architecture.md)
- [APIリファレンス](./api-reference.md)
- [データベーススキーマ](./database-schema.md)

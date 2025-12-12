# Act 01: RAG基盤実装（Phase 1完了）

**実装日**: 2025年12月10日
**ステータス**: ✅ 完了

---

## 概要

LangChainベースのAIチャット機能のための基盤を実装しました。2層RAG構造（実績RAG + ナレッジRAG）の基礎となるデータモデル、ベクトル化サービス、ドキュメント処理機能を完成させました。

---

## 実装内容

### 1. データモデル (ai_features/models.py)

#### DocumentVector - 実績RAG用
```python
class DocumentVector(models.Model):
    """日報・掲示板・実績データのベクトル表現"""
    vector_id = AutoField(primary_key=True)
    source_type = CharField  # 'daily_report' | 'bbs_post' | 'bbs_comment' | 'performance'
    source_id = IntegerField
    content = TextField
    metadata = JSONField  # store_id, user_id, date, genre, etc.
    embedding = VectorField(dimensions=384)  # sentence-transformers
    created_at, updated_at

    # インデックス: (source_type, source_id), created_at
    # unique_together: (source_type, source_id)
```

#### KnowledgeDocument - マニュアル原本管理
```python
class KnowledgeDocument(models.Model):
    """業務マニュアル・規則の原本管理"""
    document_id = AutoField(primary_key=True)
    document_type = CharField  # 'manual' | 'guideline' | 'faq' | 'policy'
    title = CharField(max_length=200)
    category = CharField  # 'hygiene' | 'service' | 'cooking' | 'safety' | 'other'

    # ファイル情報
    file_path = FileField(upload_to='knowledge/')
    file_type = CharField  # 'pdf' | 'docx' | 'md'

    # バージョン管理
    version = CharField
    is_active = BooleanField(default=True)

    # ベクトル化状態
    vectorized = BooleanField(default=False)
    vectorized_at = DateTimeField(null=True)
```

#### KnowledgeVector - ナレッジRAG用
```python
class KnowledgeVector(models.Model):
    """マニュアルのベクトル表現（チャンク単位）"""
    vector_id = AutoField(primary_key=True)
    document = ForeignKey(KnowledgeDocument)
    document_type = CharField
    content = TextField  # チャンク（500-1000トークン）
    metadata = JSONField  # category, chapter, section, version, etc.
    embedding = VectorField(dimensions=384)
    created_at, updated_at

    # インデックス: document_type, created_at
```

### 2. ドキュメント処理サービス

#### DocumentParser (ai_features/services/document_parser.py)
```python
class DocumentParser:
    """PDF、Word、Markdownからテキスト抽出"""

    @classmethod
    def extract_text(file_path: str, file_type: str) -> str:
        """ファイル種別に応じてテキスト抽出"""

    @classmethod
    def extract_from_pdf(file_path: str) -> str:
        """PDFからページ番号付きでテキスト抽出"""

    @classmethod
    def extract_from_docx(file_path: str) -> str:
        """Wordからパラグラフ・テーブル抽出"""

    @classmethod
    def extract_from_markdown(file_path: str) -> str:
        """Markdownファイル読み込み"""

    @classmethod
    def extract_metadata_from_pdf(file_path: str) -> dict:
        """PDFメタデータ抽出（title, author, etc.）"""
```

**実装ライブラリ**:
- `PyPDF2`: PDF処理
- `python-docx`: Word処理
- `markdown`: Markdown処理

#### KnowledgeChunker (ai_features/services/knowledge_chunker.py)
```python
class KnowledgeChunker:
    """マニュアル専用チャンキング"""

    MIN_CHUNK_SIZE = 500   # トークン
    MAX_CHUNK_SIZE = 1000  # トークン
    OVERLAP_SIZE = 100     # トークン
    CHARS_PER_TOKEN = 4    # 日本語の概算

    @classmethod
    def chunk_text(text: str, preserve_structure: bool = True) -> List[Dict]:
        """構造を考慮したチャンキング"""

    @classmethod
    def _chunk_with_structure(text: str) -> List[Dict]:
        """章・節の見出しを認識してセマンティック境界で分割"""

    @classmethod
    def _extract_sections(text: str) -> List[Dict]:
        """章・節パターン認識（第1章、1.1、## など）"""
```

**特徴**:
- 実績データ（200-400トークン）より大きめのチャンクサイズ
- セマンティック境界保持（章・節区切り）
- 100トークンのオーバーラップ
- 日本語対応

### 3. コアサービス (ai_features/services.py)

#### EmbeddingService
```python
class EmbeddingService:
    """sentence-transformersでローカルベクトル生成"""

    MODEL_NAME = 'paraphrase-multilingual-MiniLM-L12-v2'
    DIMENSION = 384

    @classmethod
    def generate_embedding(text: str) -> List[float]:
        """テキスト → 384次元ベクトル"""

    @classmethod
    def generate_embeddings_batch(texts: List[str]) -> List[List[float]]:
        """バッチ処理でベクトル生成"""
```

**特徴**:
- 日本語対応モデル
- シングルトンパターン（モデルの再ロード防止）
- バッチ処理対応

#### VectorizationService
```python
class VectorizationService:
    """DocumentVectorへの保存サービス"""

    @classmethod
    def vectorize_daily_report(report_id: int) -> bool:
        """日報ベクトル化"""

    @classmethod
    def vectorize_bbs_post(post_id: int) -> bool:
        """掲示板投稿ベクトル化"""

    @classmethod
    def vectorize_bbs_comment(comment_id: int) -> bool:
        """掲示板コメントベクトル化"""
```

**メタデータ例（日報）**:
```python
{
    'store_id': 1,
    'store_name': '○○店',
    'user_id': 'S001',
    'user_name': '佐藤太郎',
    'date': '2025-12-10',
    'has_claim': True,
    'has_praise': False,
    'has_accident': False
}
```

### 4. 管理コマンド

#### vectorize_knowledge (ai_features/management/commands/)
```bash
# 全マニュアルをベクトル化
python manage.py vectorize_knowledge --all

# 特定のドキュメントをベクトル化
python manage.py vectorize_knowledge --document-id 1

# 未ベクトル化のみ処理
python manage.py vectorize_knowledge --unvectorized

# 強制再ベクトル化
python manage.py vectorize_knowledge --all --force
```

**機能**:
- KnowledgeDocumentのベクトル化処理
- DocumentParser → KnowledgeChunker → EmbeddingService の連携
- 進捗表示（tqdm）
- エラーハンドリング
- ベクトル化状態の管理

**処理フロー**:
```
1. KnowledgeDocument取得
2. ファイルからテキスト抽出（DocumentParser）
3. チャンキング（KnowledgeChunker）
4. 各チャンクをベクトル化（EmbeddingService）
5. KnowledgeVectorに保存
6. documentのvectorizedフラグ更新
```

### 5. インフラ設定

#### PostgreSQL + PgVector
```yaml
# docker-compose.yml
services:
  postgres:
    image: pgvector/pgvector:pg17  # ← postgres:17-alpineから変更
    volumes:
      - ./init-pgvector.sql:/docker-entrypoint-initdb.d/init-pgvector.sql
```

#### マイグレーション
```python
# 0002_knowledgedocument_documentvector_knowledgevector.py
operations = [
    # pgvector拡張を有効化
    migrations.RunSQL(
        sql="CREATE EXTENSION IF NOT EXISTS vector;",
        reverse_sql="DROP EXTENSION IF EXISTS vector CASCADE;",
    ),
    # ... モデル作成
]
```

#### 依存関係 (requirements.txt)
```txt
# AI Features - RAG & Vector Search
sentence-transformers>=2.2.0
torch>=2.0.0
pgvector>=0.2.0
google-generativeai>=0.3.0

# Document Processing (Phase 1)
pypdf2>=3.0.0
python-docx>=1.0.0
markdown>=3.5.0

# LangChain (Phase 2/3)
langchain>=0.1.0
langchain-community>=0.0.20
langchain-openai>=0.0.5
```

---

## ファイル構成

```
c3_app/
├── ai_features/
│   ├── models.py                           # ✅ 3つのモデル追加
│   ├── services.py                         # ✅ EmbeddingService, VectorizationService
│   ├── services/
│   │   ├── __init__.py                     # ✅ 新規作成
│   │   ├── document_parser.py              # ✅ 新規作成
│   │   └── knowledge_chunker.py            # ✅ 新規作成
│   ├── management/
│   │   └── commands/
│   │       └── vectorize_knowledge.py      # ✅ 新規作成
│   └── migrations/
│       └── 0002_*.py                       # ✅ pgvector拡張有効化追加
├── docker-compose.yml                      # ✅ pgvectorイメージに変更
├── init-pgvector.sql                       # (既存)
├── requirements.txt                        # ✅ 依存関係追加
├── plan.md                                 # ✅ 詳細設計書
└── act01.md                                # 📄 このファイル
```

---

## データベーススキーマ

### document_vectors テーブル
| カラム | 型 | 説明 |
|--------|-----|------|
| vector_id | SERIAL | PRIMARY KEY |
| source_type | VARCHAR(20) | 'daily_report', 'bbs_post', etc. |
| source_id | INTEGER | ソースのID |
| content | TEXT | テキストコンテンツ |
| metadata | JSONB | メタデータ |
| embedding | VECTOR(384) | 埋め込みベクトル |
| created_at | TIMESTAMP | 作成日時 |
| updated_at | TIMESTAMP | 更新日時 |

**インデックス**:
- `(source_type, source_id)` - ユニーク制約
- `created_at`

### knowledge_documents テーブル
| カラム | 型 | 説明 |
|--------|-----|------|
| document_id | SERIAL | PRIMARY KEY |
| document_type | VARCHAR(20) | 'manual', 'guideline', etc. |
| title | VARCHAR(200) | タイトル |
| category | VARCHAR(20) | 'hygiene', 'service', etc. |
| file_path | VARCHAR(255) | ファイルパス |
| file_type | VARCHAR(10) | 'pdf', 'docx', 'md' |
| version | VARCHAR(50) | バージョン |
| is_active | BOOLEAN | 有効フラグ |
| vectorized | BOOLEAN | ベクトル化済みフラグ |
| vectorized_at | TIMESTAMP | ベクトル化日時 |
| created_at | TIMESTAMP | 作成日時 |
| updated_at | TIMESTAMP | 更新日時 |

### knowledge_vectors テーブル
| カラム | 型 | 説明 |
|--------|-----|------|
| vector_id | SERIAL | PRIMARY KEY |
| document_id | INTEGER | FOREIGN KEY → knowledge_documents |
| document_type | VARCHAR(20) | ドキュメント種別 |
| content | TEXT | チャンクコンテンツ |
| metadata | JSONB | メタデータ |
| embedding | VECTOR(384) | 埋め込みベクトル |
| created_at | TIMESTAMP | 作成日時 |
| updated_at | TIMESTAMP | 更新日時 |

**インデックス**:
- `document_type`
- `created_at`

---

## 技術スタック

| カテゴリ | 技術 | 用途 |
|----------|------|------|
| Web Framework | Django 5.2.4 | Webアプリケーション |
| Database | PostgreSQL 17 + PgVector | ベクトルDB |
| Embedding | sentence-transformers | ローカルベクトル生成 |
| | paraphrase-multilingual-MiniLM-L12-v2 | 日本語対応モデル（384次元） |
| Document Processing | PyPDF2 | PDF解析 |
| | python-docx | Word解析 |
| | markdown | Markdown処理 |
| Container | Docker | PostgreSQL環境 |

---

## 設計上の重要ポイント

### 1. 2層RAG構造の基礎
- **実績RAG** (DocumentVector): 日報・掲示板・実績データ
- **ナレッジRAG** (KnowledgeVector): マニュアル・規則・FAQ

**分離理由**:
- 検索意図が異なる（過去事例 vs 正式手順）
- 更新頻度が違う（毎日 vs 月次）
- メタデータ構造が違う（日付・店舗 vs 章・節・バージョン）
- チャンク戦略が違う（小 vs 大）

### 2. チャンキング戦略
- **実績データ**: 200-400トークン（将来実装）
- **マニュアル**: 500-1000トークン（今回実装）
- オーバーラップ: 100トークン
- 構造保持: 章・節区切りを考慮

### 3. ベクトル次元
- 384次元（paraphrase-multilingual-MiniLM-L12-v2）
- 理由: 日本語対応、バランスの良いサイズ、高速処理

### 4. メタデータ設計
実績データとナレッジで異なるメタデータ構造:

**実績RAG**:
```json
{
  "store_id": 1,
  "user_id": "S001",
  "date": "2025-12-10",
  "genre": "claim"
}
```

**ナレッジRAG**:
```json
{
  "category": "hygiene",
  "document_title": "衛生管理マニュアル 第3版",
  "chapter": "第5章",
  "section": "5.2 フライヤー管理",
  "version": "2024-12"
}
```

---

## 次のステップ (Phase 2)

### Phase 2: ツール実装（3-4日予定）

1. **検索ツール3個**:
   - `search_past_cases()`: 過去事例検索（直接検索）
   - `expand_and_search_cases()`: クエリ拡張 + 並列検索
   - `search_manual()`: マニュアル検索

2. **統計ツール4個**:
   - `get_claim_statistics()`: クレーム統計
   - `get_sales_trend()`: 売上推移
   - `get_cash_difference_analysis()`: 違算分析
   - `compare_periods()`: 期間比較

3. **サポート機能**:
   - Query Expansion（LLMベースのクエリ拡張）
   - Result Merger（検索結果統合・ランキング）

### Phase 3: LangChain Agent（2-3日予定）

1. Ollamaセットアップ
2. Function Calling Agent実装
3. プロンプトエンジニアリング

---

## 課題・改善点

### 今後の拡張予定

1. **IVFFlat インデックス作成** (パフォーマンス最適化)
```sql
CREATE INDEX document_vectors_embedding_idx
ON document_vectors
USING ivfflat (embedding vector_cosine_ops)
WITH (lists = 100);
```

2. **動的Top-K決定機能** (QueryClassifier)
   - クエリの性質に応じて取得件数を調整（3-20件）

3. **バッチベクトル化の並列処理**
   - 大量ドキュメント処理の高速化

4. **ベクトル検索サービス** (VectorSearchService)
   - Phase 2で実装予定
   - PgVectorのコサイン類似度検索
   - メタデータフィルタリング

---

## まとめ

Phase 1では、LangChainベースのAIチャット機能のための**RAG基盤**を完成させました。

**達成したこと**:
- ✅ 2層RAG構造のデータモデル
- ✅ PDF/Word/Markdown対応のドキュメント処理
- ✅ 構造保持型チャンキング
- ✅ sentence-transformersベクトル化
- ✅ PostgreSQL + PgVector環境
- ✅ マニュアルベクトル化コマンド

これで、マニュアルファイルをアップロードしてベクトル化できる基盤が整いました。次のPhase 2では、この基盤を活用した検索ツールと統計ツールを実装していきます。

---

**実装者ノート**:
Phase 1の実装は順調に完了。マイグレーションでpgvector拡張を自動有効化する工夫により、Docker環境のセットアップがスムーズになった。Phase 2では、ベクトル検索サービスとクエリ拡張機能の実装が重要。

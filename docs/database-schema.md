# データベーススキーマ

本ドキュメントでは、C3 ステリコットαのデータベース構造を記載します。

---

## 概要

- **データベース**: PostgreSQL 17
- **拡張**: pgvector（ベクトル検索用）
- **ORM**: Django ORM

---

## ER図

```
┌─────────────────┐
│     stores      │
├─────────────────┤
│ PK store_id     │
│    store_name   │
│    address      │
│ FK manager      │───┐
│    created_at   │   │
└────────┬────────┘   │
         │            │
         │            │
         ▼            │
┌─────────────────┐   │
│     users       │◀──┘
├─────────────────┤
│ PK user_id      │
│ FK store        │
│    user_type    │
│    email        │
│    last_name    │
│    first_name   │
│    is_active    │
│    created_at   │
└────────┬────────┘
         │
         │
    ┌────┴────┬─────────────┬──────────────┐
    │         │             │              │
    ▼         ▼             ▼              ▼
┌─────────┐ ┌─────────┐ ┌─────────┐ ┌─────────────┐
│ daily   │ │ bbs     │ │ bbs     │ │ ai_chat     │
│ reports │ │ posts   │ │ comments│ │ history     │
└────┬────┘ └────┬────┘ └─────────┘ └─────────────┘
     │           │
     │           │
     ▼           ▼
┌─────────┐ ┌─────────┐
│ report  │ │ bbs     │
│ images  │ │ reactions│
└─────────┘ └─────────┘
```

---

## テーブル定義

### stores（店舗）

店舗の基本情報を管理します。

| カラム | 型 | NULL | デフォルト | 説明 |
|--------|------|------|------------|------|
| `store_id` | SERIAL | NO | AUTO | 主キー |
| `store_name` | VARCHAR(100) | NO | - | 店舗名 |
| `address` | VARCHAR(255) | NO | - | 住所 |
| `manager` | VARCHAR(20) | YES | NULL | 管理者ユーザーID（FK → users） |
| `created_at` | TIMESTAMP | NO | NOW() | 作成日時 |

**インデックス**:
- PRIMARY KEY (`store_id`)

**外部キー**:
- `manager` → `users.user_id` (ON DELETE SET NULL)

---

### users（ユーザー）

システムのユーザー情報を管理します。Django認証と統合。

| カラム | 型 | NULL | デフォルト | 説明 |
|--------|------|------|------------|------|
| `user_id` | VARCHAR(20) | NO | - | 主キー（ログインID） |
| `store` | INTEGER | NO | - | 所属店舗ID（FK → stores） |
| `user_type` | VARCHAR(20) | NO | 'staff' | ユーザー種別 |
| `email` | VARCHAR(254) | YES | NULL | メールアドレス（UNIQUE） |
| `last_name` | VARCHAR(50) | NO | '' | 姓 |
| `first_name` | VARCHAR(50) | NO | '' | 名 |
| `password` | VARCHAR(128) | NO | - | ハッシュ化パスワード |
| `is_active` | BOOLEAN | NO | TRUE | アカウント有効フラグ |
| `is_staff` | BOOLEAN | NO | FALSE | Django管理画面アクセス権限 |
| `is_superuser` | BOOLEAN | NO | FALSE | スーパーユーザー権限 |
| `created_at` | TIMESTAMP | NO | NOW() | 作成日時 |
| `login_at` | TIMESTAMP | YES | NULL | 最終ログイン日時 |
| `last_access_at` | TIMESTAMP | YES | NULL | 最終アクセス日時 |

**user_type選択肢**:
| 値 | 説明 |
|------|------|
| `staff` | スタッフ |
| `manager` | 店長 |
| `admin` | 管理者 |

**インデックス**:
- PRIMARY KEY (`user_id`)
- UNIQUE (`email`)

**外部キー**:
- `store` → `stores.store_id` (ON DELETE PROTECT)

---

### monthly_goals（月次目標）

店舗ごとの月次目標を管理します。

| カラム | 型 | NULL | デフォルト | 説明 |
|--------|------|------|------------|------|
| `goal_id` | SERIAL | NO | AUTO | 主キー |
| `store` | INTEGER | NO | - | 店舗ID（FK → stores） |
| `year` | INTEGER | NO | - | 年 |
| `month` | INTEGER | NO | - | 月（1-12） |
| `goal_text` | TEXT | NO | - | 目標内容 |
| `achievement_rate` | INTEGER | NO | 0 | 達成率（0-100%） |
| `achievement_text` | TEXT | NO | '' | 達成状況コメント |
| `created_at` | TIMESTAMP | NO | NOW() | 作成日時 |
| `updated_at` | TIMESTAMP | NO | NOW() | 更新日時 |

**インデックス**:
- PRIMARY KEY (`goal_id`)
- UNIQUE (`store`, `year`, `month`)

**外部キー**:
- `store` → `stores.store_id` (ON DELETE CASCADE)

---

### daily_reports（日報）

日報の情報を管理します。

| カラム | 型 | NULL | デフォルト | 説明 |
|--------|------|------|------------|------|
| `report_id` | SERIAL | NO | AUTO | 主キー |
| `store` | INTEGER | NO | - | 店舗ID（FK → stores） |
| `user` | VARCHAR(20) | YES | NULL | 作成者ユーザーID（FK → users） |
| `date` | DATE | NO | - | 日報日付 |
| `genre` | VARCHAR(20) | NO | - | ジャンル |
| `location` | VARCHAR(20) | NO | - | 場所 |
| `title` | VARCHAR(200) | NO | - | 件名 |
| `content` | TEXT | NO | - | 内容 |
| `post_to_bbs` | BOOLEAN | NO | FALSE | 掲示板連携フラグ |
| `created_at` | TIMESTAMP | NO | NOW() | 作成日時 |

**genre選択肢**:
| 値 | 説明 |
|------|------|
| `claim` | クレーム |
| `praise` | 賞賛 |
| `accident` | 事故 |
| `report` | 報告 |
| `other` | その他 |

**location選択肢**:
| 値 | 説明 |
|------|------|
| `kitchen` | キッチン |
| `hall` | ホール |
| `cashier` | レジ |
| `toilet` | トイレ |
| `other` | その他 |

**インデックス**:
- PRIMARY KEY (`report_id`)
- INDEX (`store`, `date`)
- INDEX (`date`)

**外部キー**:
- `store` → `stores.store_id` (ON DELETE CASCADE)
- `user` → `users.user_id` (ON DELETE SET NULL)

---

### report_images（日報画像）

日報に添付された画像を管理します。

| カラム | 型 | NULL | デフォルト | 説明 |
|--------|------|------|------------|------|
| `image_id` | SERIAL | NO | AUTO | 主キー |
| `report` | INTEGER | NO | - | 日報ID（FK → daily_reports） |
| `file_path` | VARCHAR(255) | NO | - | ファイルパス |
| `uploaded_at` | TIMESTAMP | NO | NOW() | アップロード日時 |

**ファイルパス形式**:
```
reports/store_{store_id}/{year}/{month:02d}/{day:02d}/{uuid}.{ext}
```

**インデックス**:
- PRIMARY KEY (`image_id`)

**外部キー**:
- `report` → `daily_reports.report_id` (ON DELETE CASCADE)

---

### store_daily_performances（店舗日次実績）

店舗の日次売上・客数などの実績を管理します。

| カラム | 型 | NULL | デフォルト | 説明 |
|--------|------|------|------------|------|
| `performance_id` | SERIAL | NO | AUTO | 主キー |
| `store` | INTEGER | NO | - | 店舗ID（FK → stores） |
| `date` | DATE | NO | - | 日付 |
| `sales_amount` | INTEGER | NO | - | 売上金額（円） |
| `customer_count` | INTEGER | NO | - | 客数 |
| `cash_difference` | INTEGER | NO | 0 | 違算金額（円） |
| `registered_by` | VARCHAR(20) | YES | NULL | 登録者（FK → users） |
| `created_at` | TIMESTAMP | NO | NOW() | 作成日時 |
| `updated_at` | TIMESTAMP | NO | NOW() | 更新日時 |

**インデックス**:
- PRIMARY KEY (`performance_id`)
- UNIQUE (`store`, `date`)
- INDEX (`date`)

**外部キー**:
- `store` → `stores.store_id` (ON DELETE CASCADE)
- `registered_by` → `users.user_id` (ON DELETE SET NULL)

---

### bbs_posts（掲示板投稿）

掲示板の投稿を管理します。

| カラム | 型 | NULL | デフォルト | 説明 |
|--------|------|------|------------|------|
| `post_id` | SERIAL | NO | AUTO | 主キー |
| `store` | INTEGER | NO | - | 店舗ID（FK → stores） |
| `user` | VARCHAR(20) | NO | - | 投稿者（FK → users） |
| `report` | INTEGER | YES | NULL | 関連日報ID（FK → daily_reports） |
| `genre` | VARCHAR(20) | NO | 'report' | ジャンル |
| `title` | VARCHAR(200) | NO | - | タイトル |
| `content` | TEXT | NO | - | 本文 |
| `comment_count` | INTEGER | NO | 0 | コメント数 |
| `created_at` | TIMESTAMP | NO | NOW() | 投稿日時 |
| `updated_at` | TIMESTAMP | NO | NOW() | 更新日時 |

**インデックス**:
- PRIMARY KEY (`post_id`)
- INDEX (`created_at`)

**外部キー**:
- `store` → `stores.store_id` (ON DELETE CASCADE)
- `user` → `users.user_id` (ON DELETE CASCADE)
- `report` → `daily_reports.report_id` (ON DELETE SET NULL)

---

### bbs_comments（掲示板コメント）

掲示板投稿へのコメントを管理します。

| カラム | 型 | NULL | デフォルト | 説明 |
|--------|------|------|------------|------|
| `comment_id` | SERIAL | NO | AUTO | 主キー |
| `post` | INTEGER | NO | - | 投稿ID（FK → bbs_posts） |
| `user` | VARCHAR(20) | NO | - | コメント者（FK → users） |
| `content` | TEXT | NO | - | コメント内容 |
| `is_best_answer` | BOOLEAN | NO | FALSE | ベストアンサーフラグ |
| `created_at` | TIMESTAMP | NO | NOW() | 投稿日時 |
| `updated_at` | TIMESTAMP | NO | NOW() | 更新日時 |

**インデックス**:
- PRIMARY KEY (`comment_id`)
- INDEX (`post`)

**外部キー**:
- `post` → `bbs_posts.post_id` (ON DELETE CASCADE)
- `user` → `users.user_id` (ON DELETE CASCADE)

---

### bbs_reactions（掲示板リアクション）

投稿へのリアクションを管理します。

| カラム | 型 | NULL | デフォルト | 説明 |
|--------|------|------|------------|------|
| `reaction_id` | SERIAL | NO | AUTO | 主キー |
| `post` | INTEGER | NO | - | 投稿ID（FK → bbs_posts） |
| `user` | VARCHAR(20) | NO | - | リアクション者（FK → users） |
| `reaction_type` | VARCHAR(20) | NO | - | リアクション種別 |
| `created_at` | TIMESTAMP | NO | NOW() | 作成日時 |

**reaction_type選択肢**:
| 値 | 説明 |
|------|------|
| `naruhodo` | なるほど |
| `iine` | いいね |

**インデックス**:
- PRIMARY KEY (`reaction_id`)
- UNIQUE (`post`, `user`, `reaction_type`)

**外部キー**:
- `post` → `bbs_posts.post_id` (ON DELETE CASCADE)
- `user` → `users.user_id` (ON DELETE CASCADE)

---

### bbs_comment_reactions（コメントリアクション）

コメントへのリアクションを管理します。

| カラム | 型 | NULL | デフォルト | 説明 |
|--------|------|------|------------|------|
| `reaction_id` | SERIAL | NO | AUTO | 主キー |
| `comment` | INTEGER | NO | - | コメントID（FK → bbs_comments） |
| `user` | VARCHAR(20) | NO | - | リアクション者（FK → users） |
| `reaction_type` | VARCHAR(20) | NO | - | リアクション種別 |
| `created_at` | TIMESTAMP | NO | NOW() | 作成日時 |

**インデックス**:
- PRIMARY KEY (`reaction_id`)
- UNIQUE (`comment`, `user`, `reaction_type`)

**外部キー**:
- `comment` → `bbs_comments.comment_id` (ON DELETE CASCADE)
- `user` → `users.user_id` (ON DELETE CASCADE)

---

### ai_chat_history（AIチャット履歴）

AIチャットの会話履歴を管理します。

| カラム | 型 | NULL | デフォルト | 説明 |
|--------|------|------|------------|------|
| `chat_id` | SERIAL | NO | AUTO | 主キー |
| `user` | VARCHAR(20) | NO | - | ユーザーID（FK → users） |
| `role` | VARCHAR(20) | NO | - | 役割（user/assistant） |
| `message` | TEXT | NO | - | メッセージ内容 |
| `created_at` | TIMESTAMP | NO | NOW() | 作成日時 |

**role選択肢**:
| 値 | 説明 |
|------|------|
| `user` | ユーザー |
| `assistant` | AI |

**インデックス**:
- PRIMARY KEY (`chat_id`)
- INDEX (`user`, `created_at`)

**外部キー**:
- `user` → `users.user_id` (ON DELETE CASCADE)

---

### document_vectors（ドキュメントベクトル）

RAG用のドキュメントベクトルを管理します。

| カラム | 型 | NULL | デフォルト | 説明 |
|--------|------|------|------------|------|
| `vector_id` | SERIAL | NO | AUTO | 主キー |
| `source_type` | VARCHAR(20) | NO | - | ソース種別 |
| `source_id` | INTEGER | NO | - | ソースID |
| `content` | TEXT | NO | - | コンテンツ |
| `metadata` | JSONB | NO | {} | メタデータ |
| `embedding` | VECTOR(384) | NO | - | 埋め込みベクトル |
| `created_at` | TIMESTAMP | NO | NOW() | 作成日時 |
| `updated_at` | TIMESTAMP | NO | NOW() | 更新日時 |

**source_type選択肢**:
| 値 | 説明 |
|------|------|
| `daily_report` | 日報 |
| `bbs_post` | 掲示板投稿 |
| `bbs_comment` | 掲示板コメント |
| `performance` | 店舗実績 |

**metadata例**:
```json
{
  "store_id": 1,
  "date": "2024-01-15",
  "title": "クレーム対応について",
  "genre": "claim"
}
```

**インデックス**:
- PRIMARY KEY (`vector_id`)
- UNIQUE (`source_type`, `source_id`)
- INDEX (`source_type`, `source_id`)
- INDEX (`created_at`)

---

### knowledge_vectors（ナレッジベクトル）

マニュアルやFAQなどのナレッジベースを管理します。

| カラム | 型 | NULL | デフォルト | 説明 |
|--------|------|------|------------|------|
| `vector_id` | SERIAL | NO | AUTO | 主キー |
| `document_type` | VARCHAR(20) | NO | - | ドキュメント種別 |
| `title` | VARCHAR(200) | NO | - | タイトル |
| `content` | TEXT | NO | - | コンテンツ |
| `metadata` | JSONB | NO | {} | メタデータ |
| `embedding` | VECTOR(384) | NO | - | 埋め込みベクトル |
| `created_at` | TIMESTAMP | NO | NOW() | 作成日時 |
| `updated_at` | TIMESTAMP | NO | NOW() | 更新日時 |

**document_type選択肢**:
| 値 | 説明 |
|------|------|
| `manual` | マニュアル |
| `faq` | FAQ |
| `policy` | ポリシー |
| `guide` | ガイド |
| `other` | その他 |

**インデックス**:
- PRIMARY KEY (`vector_id`)
- INDEX (`document_type`)
- INDEX (`created_at`)

---

## マイグレーション

マイグレーションはDjango標準のマイグレーション機能を使用します。

```bash
# マイグレーションファイル作成
python manage.py makemigrations

# マイグレーション実行
python manage.py migrate

# マイグレーション状態確認
python manage.py showmigrations
```

---

## 関連ドキュメント

- [システムアーキテクチャ](./architecture.md)
- [APIリファレンス](./api-reference.md)
- [デプロイガイド](./deployment.md)

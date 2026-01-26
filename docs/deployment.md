# デプロイガイド

本ドキュメントでは、C3 ステリコットαの本番環境へのデプロイ手順を記載します。

---

## 概要

本システムは以下のサービスを使用してデプロイされます。

| サービス | 用途 |
|----------|------|
| **Render** | Webアプリケーションホスティング |
| **Supabase** | PostgreSQLデータベース、ストレージ |
| **OpenAI** | AI機能（GPT-4o-mini） |

---

## アーキテクチャ

```
┌─────────────────────────────────────────────┐
│                  Render                      │
│  ┌─────────────────┐  ┌─────────────────┐   │
│  │   c3-app        │  │  c3-app-stream  │   │
│  │   (Gunicorn)    │  │  (Uvicorn)      │   │
│  └────────┬────────┘  └────────┬────────┘   │
└───────────┼─────────────────────┼───────────┘
            │                     │
            └──────────┬──────────┘
                       │
            ┌──────────▼──────────┐
            │      Supabase       │
            │  PostgreSQL + S3    │
            └─────────────────────┘
```

---

## 前提条件

### 必要なアカウント

1. **Render** アカウント（https://render.com）
2. **Supabase** アカウント（https://supabase.com）
3. **OpenAI** アカウント（https://platform.openai.com）
4. **GitHub** アカウント（リポジトリ連携用）

---

## Supabaseセットアップ

### 1. プロジェクト作成

1. Supabase Dashboardにログイン
2. "New Project" をクリック
3. プロジェクト情報を入力
   - **Name**: `c3-app`
   - **Database Password**: 強力なパスワードを設定
   - **Region**: Tokyo（ap-northeast-1）推奨

### 2. pgvector拡張の有効化

1. SQL Editorを開く
2. 以下のSQLを実行

```sql
CREATE EXTENSION IF NOT EXISTS vector;
```

### 3. データベース接続情報の取得

1. Settings → Database に移動
2. 以下の情報をメモ
   - **Host**: `xxx.supabase.co`
   - **Database name**: `postgres`
   - **Port**: `5432`
   - **User**: `postgres`
   - **Password**: プロジェクト作成時に設定したもの

### 4. Storage設定

1. Storage → Create a new bucket
2. バケット名: `media`
3. Public bucket: ON

### 5. S3互換API認証情報の取得

1. Settings → API
2. "Generate new S3 access keys" をクリック
3. 以下をメモ
   - **Access Key ID**
   - **Secret Access Key**

---

## Renderセットアップ

### 1. GitHubリポジトリ連携

1. Render Dashboardにログイン
2. "New" → "Blueprint" を選択
3. GitHubリポジトリを選択

### 2. render.yamlによる自動設定

`render.yaml`ファイルにより、以下が自動作成されます：

- **c3-app**: メインWebサービス
- **c3-app-stream**: ストリーミングサービス

### 3. 環境変数設定

各サービスのEnvironment設定で以下を設定：

#### c3-app（メインサービス）

| 変数名 | 値 | 説明 |
|--------|------|------|
| `SECRET_KEY` | 自動生成 | Djangoセキュリティキー |
| `DEBUG` | `False` | デバッグモード |
| `ALLOWED_HOSTS` | `c3-app.onrender.com` | 許可ホスト |
| `CSRF_TRUSTED_ORIGINS` | `https://c3-app.onrender.com` | CSRF許可オリジン |
| `SUPABASE_DB_NAME` | `postgres` | DB名 |
| `SUPABASE_DB_USER` | `postgres` | DBユーザー |
| `SUPABASE_DB_PASSWORD` | （Supabaseで設定したもの） | DBパスワード |
| `SUPABASE_DB_HOST` | `xxx.supabase.co` | DBホスト |
| `SUPABASE_DB_PORT` | `5432` | DBポート |
| `OPENAI_API_KEY` | `sk-xxx...` | OpenAI APIキー |
| `OPENAI_MODEL` | `gpt-4o-mini` | 使用モデル |
| `MAX_CHAT_HISTORY` | `14` | チャット履歴保持数 |
| `STREAM_API_URL` | `https://c3-app-stream.onrender.com` | ストリーミングサーバーURL |
| `SUPABASE_PROJECT_ID` | （プロジェクトID） | SupabaseプロジェクトID |
| `SUPABASE_STORAGE_ACCESS_KEY` | （取得したもの） | S3アクセスキー |
| `SUPABASE_STORAGE_SECRET_KEY` | （取得したもの） | S3シークレットキー |
| `SUPABASE_STORAGE_BUCKET` | `media` | バケット名 |

#### c3-app-stream（ストリーミングサービス）

メインサービスと同様の環境変数を設定（STREAM_API_URLは不要）

### 4. 初回デプロイ

1. Render Dashboardで "Deploy" をクリック
2. ビルドログを確認
3. マイグレーションが自動実行される

### 5. スーパーユーザー作成（初回のみ）

Renderのシェルから実行：

```bash
python manage.py createsuperuser
```

または環境変数を設定して自動作成：

| 変数名 | 値 |
|--------|------|
| `DJANGO_SUPERUSER_USER_ID` | 管理者ID |
| `DJANGO_SUPERUSER_PASSWORD` | パスワード |
| `DJANGO_SUPERUSER_EMAIL` | メールアドレス |

---

## CI/CD設定

### GitHub Actions

`.github/workflows/ci.yml`により、以下が自動実行されます：

1. **Push/PR時**: テスト実行
2. **mainブランチマージ時**: 自動デプロイ

### デプロイフロー

```
GitHub (push to main)
    │
    ▼
GitHub Actions (test)
    │
    ▼ (成功時)
Render (webhook trigger)
    │
    ▼
ビルド＆デプロイ
    │
    ▼
マイグレーション実行
```

---

## ビルドスクリプト

### build.sh

```bash
#!/usr/bin/env bash
set -o errexit

pip install -r requirements.txt
python manage.py collectstatic --no-input
python manage.py migrate
```

### start_stream.sh

```bash
#!/usr/bin/env bash
exec uvicorn asgi_stream:app \
    --host 0.0.0.0 \
    --port ${PORT:-8001} \
    --timeout-keep-alive 300
```

---

## 運用コマンド

### Renderシェルでの操作

```bash
# マイグレーション実行
python manage.py migrate

# データベースシェル
python manage.py dbshell

# スーパーユーザー作成
python manage.py createsuperuser

# 管理コマンド実行
python manage.py <command>
```

### デモデータのセットアップ

環境変数 `RUN_DEMO_SETUP=true` を設定して再デプロイ：

```bash
# build.sh内で自動実行される
python manage.py seed
```

---

## トラブルシューティング

### データベース接続エラー

**症状**: `connection refused` または `timeout`

**対処法**:
1. Supabase DashboardでDB状態を確認
2. 環境変数の値を再確認（特にパスワード）
3. SSLモード設定を確認（`sslmode=require`）

### 静的ファイルが表示されない

**症状**: CSS/JSが読み込まれない

**対処法**:
1. `collectstatic`が実行されているか確認
2. WhiteNoise設定を確認
3. `STATIC_URL`と`STATIC_ROOT`の設定を確認

### ストリーミングが動作しない

**症状**: チャットの応答が返ってこない

**対処法**:
1. `STREAM_API_URL`が正しく設定されているか確認
2. c3-app-streamサービスが起動しているか確認
3. ログでエラーを確認

### メモリ不足エラー

**症状**: R14（Memory quota exceeded）

**対処法**:
1. Renderプランのアップグレード
2. ワーカー数の調整
3. メモリリークの調査

---

## 監視とログ

### Render Dashboard

- **Logs**: リアルタイムログ表示
- **Metrics**: CPU、メモリ使用率
- **Events**: デプロイ履歴

### ヘルスチェック

```bash
curl https://c3-app.onrender.com/health/
# {"status": "ok"}
```

### アラート設定

1. Render Settings → Notifications
2. Slack/Email通知を設定

---

## バックアップ

### データベースバックアップ

Supabase Dashboardから：
1. Settings → Database
2. "Backups" タブ
3. 手動バックアップまたは自動バックアップ設定

### pg_dump（手動）

```bash
PGPASSWORD=<password> pg_dump \
    -h <host> \
    -U postgres \
    -d postgres \
    -F c \
    -f backup.dump
```

### リストア

```bash
PGPASSWORD=<password> pg_restore \
    -h <host> \
    -U postgres \
    -d postgres \
    -F c \
    backup.dump
```

---

## セキュリティチェックリスト

- [ ] `DEBUG=False` が設定されている
- [ ] `SECRET_KEY` は安全な値が設定されている
- [ ] `ALLOWED_HOSTS` が適切に設定されている
- [ ] `CSRF_TRUSTED_ORIGINS` が設定されている
- [ ] データベースパスワードは強力なものを使用
- [ ] OpenAI APIキーは秘匿されている
- [ ] SSL接続が有効になっている

---

## 関連ドキュメント

- [システムアーキテクチャ](./architecture.md)
- [開発ガイド](./development-guide.md)
- [APIリファレンス](./api-reference.md)

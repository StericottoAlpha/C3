# ストリーミング機能のセットアップ

## 概要

このプロジェクトでは、AIチャットのストリーミング機能を別のASGIサーバー（uvicorn）で実行するように分離しています。

### アーキテクチャ

- **メインアプリ（c3-app）**: Django + gunicorn (WSGI) - 通常のリクエスト処理
- **ストリーミングアプリ（c3-app-stream）**: FastAPI + uvicorn (ASGI) - ストリーミング専用

## ローカル開発

### 1. 依存関係のインストール

```bash
pip install -r requirements.txt
```

### 2. メインアプリの起動（Django）

```bash
python manage.py runserver
```

### 3. ストリーミングサーバーの起動（別ターミナル）

```bash
./start_stream.sh
# または
python asgi_stream.py
```

デフォルトではポート8001で起動します。別のポートを使用する場合：

```bash
PORT=8002 ./start_stream.sh
```

### 4. ローカル環境での設定

`.env`ファイルに以下を設定（オプション）：

```bash
# ストリーミングサーバーが別ポートの場合
STREAM_API_URL=http://localhost:8001
```

設定しない場合は、同じサーバー（Django）のエンドポイントを使用します。

## Renderでのデプロイ

### 1. render.yamlの確認

`render.yaml`には2つのサービスが定義されています：

- `c3-app`: メインのDjangoアプリケーション
- `c3-app-stream`: ストリーミング専用サーバー

### 2. 環境変数の設定

Renderダッシュボードで以下の環境変数を設定：

#### メインアプリ（c3-app）

```
STREAM_API_URL=https://c3-app-stream.onrender.com
ALLOWED_HOSTS=c3-app.onrender.com,c3-app-stream.onrender.com
OPENAI_API_KEY=<your-key>
OPENAI_MODEL=gpt-4o-mini
MAX_CHAT_HISTORY=14
SUPABASE_DB_NAME=<db-name>
SUPABASE_DB_USER=<db-user>
SUPABASE_DB_PASSWORD=<db-password>
SUPABASE_DB_HOST=<db-host>
CSRF_TRUSTED_ORIGINS=https://c3-app.onrender.com
```

#### ストリーミングアプリ（c3-app-stream）

```
ALLOWED_HOSTS=c3-app.onrender.com,c3-app-stream.onrender.com
OPENAI_API_KEY=<your-key>
OPENAI_MODEL=gpt-4o-mini
MAX_CHAT_HISTORY=14
SUPABASE_DB_NAME=<db-name>
SUPABASE_DB_USER=<db-user>
SUPABASE_DB_PASSWORD=<db-password>
SUPABASE_DB_HOST=<db-host>
```

### 3. デプロイ

```bash
git add .
git commit -m "Add ASGI streaming server"
git push
```

Renderが自動的に2つのサービスをデプロイします。

## トラブルシューティング

### タイムアウトエラーが発生する場合

1. ストリーミングサーバー（c3-app-stream）が正常に起動しているか確認
2. `STREAM_API_URL`が正しく設定されているか確認
3. CORS設定が正しいか確認（asgi_stream.py:35-44）

### 認証エラーが発生する場合

1. セッションCookieが正しく送信されているか確認（credentials: 'include'）
2. 両方のサービスが同じデータベースを使用しているか確認
3. SECRET_KEYが両方のサービスで同じか確認（セッション復号化のため）

### ストリーミングが途中で止まる場合

1. Renderのタイムアウト設定を確認（uvicornの--timeout-keep-alive 300）
2. ネットワークの接続状況を確認
3. OpenAI APIのレート制限を確認

## ファイル構成

```
c3_app/
├── asgi_stream.py          # FastAPIストリーミングサーバー
├── start_stream.sh         # uvicorn起動スクリプト
├── c3_app/
│   └── settings.py         # STREAM_API_URL設定
├── ai_features/
│   ├── views.py            # テンプレートにstream_api_url渡し
│   └── templates/ai_features/
│       └── chat.html       # フロントエンド（ストリーミングURL使用）
└── render.yaml             # 2つのサービス定義
```

## API エンドポイント

### ストリーミングエンドポイント

```
POST /api/ai/chat/stream/
```

**リクエスト:**

```json
{
  "message": "ユーザーの質問",
  "include_history": true
}
```

**レスポンス（Server-Sent Events）:**

```
data: {"type": "start", "content": "チャットを開始します..."}

data: {"type": "content", "content": "応答の"}

data: {"type": "content", "content": "一部"}

data: {"type": "done", "content": ""}
```

**エラー:**

```
data: {"type": "error", "content": "エラーメッセージ"}
```

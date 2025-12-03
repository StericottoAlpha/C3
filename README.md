# C3 ステリコットα

レストラン日報によるPDCA支援システム

## 概要

本システムは、レストランの店舗スタッフ（アルバイト含む）が、日々の売上情報、クレー
ムや賛辞といった出来事、関連写真などを、店舗のPC やモバイル端末から即時に登録でき
るWeb アプリケーションである。複数店舗を展開する企業を対象とし、登録されたデータ
は店舗ごと、および企業全体で集計される。集約されたデータを時系列やインシデント別な
ど様々な切り口で分析し、課題やGP を可視化することで、具体的なCS 向上施策や業務改
善アクションに繋げることができる。また、掲示板機能やAI を活用することで登録された
情報から改善を図る。

### 主な機能

- **アカウント管理** (`accounts`): ユーザー認証、プロフィール管理
- **店舗管理** (`stores`): 店舗情報の管理
- **レポート** (`reports`): 各種レポートの作成・管理
- **掲示板** (`bbs`): スタッフ間のコミュニケーション
- **分析** (`analytics`): データ分析・可視化
- **AI機能** (`ai_features`): AI支援機能
- **共通機能** (`common`): ホームページ、共通コンポーネント

### 技術スタック

- **Backend**: Django 5.2.4
- **Frontend**: HTMX（動的UIをシンプルに実装）
- **Database**: PostgreSQL 17
- **Server**: Gunicorn
- **Linter**: Ruff
- **CI/CD**: GitHub Actions
- **Deployment**: Render + Supabase

## 開発環境のセットアップ

### 必要な環境

- Python 3.10以上
- Docker & Docker Compose
- Make

### 1. リポジトリのクローン

```bash
git clone <repository-url>
cd c3_app
```

### 2. 環境変数の設定

`.env`ファイルを作成します:

```bash
cp .env.example .env
```

`.env`ファイルを編集して、必要な環境変数を設定してください。

### 3. 依存パッケージのインストール

```bash
make install
```

### 4. Dockerコンテナの起動

PostgreSQLコンテナを起動します:

```bash
make docker-up
```

### 5. データベースのセットアップ

db初期化、マイグレーションとシードデータの投入:

```bash
make db-reset
```

### 6. 開発サーバーの起動

```bash
make run
```

ブラウザで http://localhost:8000/ にアクセスしてください。

## よく使うコマンド

### Makefile コマンド

```bash
# 依存パッケージのインストール
make install

# Linterの実行
make lint

# Linterの自動修正
make lint-fix

# テストの実行
make test

# マイグレーションとマイグレート
make db-update

# データベースのリセット（シードデータ投入）
make db-reset

# パスワードハッシュの生成
make hash TARGET=password123

# Dockerコンテナの操作
make docker-up      # コンテナ起動
make docker-down    # コンテナ停止
make docker-reset   # データベース完全リセット

## ボリュームも削除したいとき
docker-compose down -v

# 開発サーバーの起動
make run
```

### Django管理コマンド

```bash
# マイグレーションファイルの作成
python3 manage.py makemigrations

# マイグレーションの実行
python3 manage.py migrate

# スーパーユーザーの作成
python3 manage.py createsuperuser

# シードデータの投入
python3 manage.py seed

# Djangoシェル
python3 manage.py shell
```

## プロジェクト構成

```
c3_app/
├── c3_app/              # プロジェクト設定
│   ├── settings.py      # Django設定
│   ├── urls.py          # ルートURL設定
│   └── wsgi.py
├── accounts/            # アカウント管理アプリ
├── stores/              # 店舗管理アプリ
├── reports/             # レポートアプリ
├── bbs/                 # 掲示板アプリ
├── analytics/           # 分析アプリ
├── ai_features/         # AI機能アプリ
├── common/              # 共通機能アプリ
├── config/              # 設定・管理コマンド
│   ├── fixtures/        # シードデータ
│   └── management/
│       └── commands/
│           └── seed.py  # seedコマンド
├── static/              # 静的ファイル（共通）
├── .github/
│   └── workflows/
│       └── ci.yml       # CI/CDパイプライン
├── docker-compose.yml   # Docker設定
├── build.sh             # Renderビルドスクリプト
├── render.yaml          # Render設定
├── requirements.txt     # Python依存パッケージ
├── pyproject.toml       # Ruff設定
├── Makefile             # タスクランナー
└── .env                 # 環境変数（gitignore）
```

## アプリケーション構成

各Djangoアプリは以下の構成を持ちます:

```
app_name/
├── models.py           # データモデル
├── views.py            # ビューロジック
├── forms.py            # フォーム定義
├── services.py         # ビジネスロジック
├── serializers.py      # JSONシリアライザ（最小限）
├── urls.py             # URLルーティング
├── admin.py            # Django Admin設定
├── templates/          # テンプレート
│   └── app_name/
│       └── components/ # HTMXコンポーネント
├── static/             # 静的ファイル
│   └── app_name/
│       ├── css/
│       ├── js/
│       └── images/
└── tests/              # テスト
    ├── test_models.py
    ├── test_views.py
    ├── test_services.py
    └── test_forms.py
```

## デプロイ

### CI/CD パイプライン

mainブランチへのPRマージ時に自動デプロイされます:

1. Linterチェック（Ruff）(現在スキップ中)
2. マイグレーション
3. テスト実行
4. ✓ 成功 → Renderへ自動デプロイ

### 環境変数（本番環境）

Renderで以下の環境変数を設定してください:

- `SECRET_KEY`: Django SECRET_KEY（自動生成）
- `DEBUG`: `False`
- `ALLOWED_HOSTS`: `your-app.onrender.com`
- `DATABASE_URL`: Supabase PostgreSQL接続URL
- `CSRF_TRUSTED_ORIGINS`: `https://your-app.onrender.com`

### GitHub Secrets

GitHub Actionsで自動デプロイするため、以下のシークレットを設定:

- `RENDER_DEPLOY_HOOK_URL`: RenderのDeploy Hook URL

## 開発ガイドライン

### 責任分離の原則

- **models.py**: データ構造の定義
- **forms.py**: フォームバリデーション（メイン）
- **services.py**: ビジネスロジック
- **views.py**: リクエスト/レスポンス処理
- **serializers.py**: JSONシリアライズ（必要最小限）

### コーディング規約

- Ruffによる自動チェック・フォーマット
- 行の長さ: 100文字
- Djangoベストプラクティスに準拠

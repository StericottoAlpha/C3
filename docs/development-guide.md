# 開発ガイド

本ドキュメントでは、C3 ステリコットαのローカル開発環境構築と開発手順を記載します。

---

## 前提条件

### 必要なソフトウェア

| ソフトウェア | バージョン | 用途 |
|-------------|-----------|------|
| Python | 3.9以上 | アプリケーション実行 |
| Docker | 最新版 | PostgreSQL実行 |
| Git | 最新版 | バージョン管理 |

### 推奨エディタ

- VS Code
- PyCharm

---

## 環境構築

### 1. リポジトリのクローン

```bash
git clone https://github.com/your-org/C3.git
cd C3
```

### 2. 仮想環境の作成

```bash
python3 -m venv env
source env/bin/activate  # macOS/Linux
# または
.\env\Scripts\activate  # Windows
```

### 3. 依存パッケージのインストール

```bash
make install
# または
pip install -r requirements.txt
```

### 4. 環境変数の設定

`.env`ファイルを作成：

```bash
cp .env.example .env
```

`.env`ファイルの内容：

```env
# Django
SECRET_KEY=your-secret-key-for-development
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1

# Database (Docker PostgreSQL)
DATABASE_URL=postgresql://c3:password@localhost:5433/c3_app_dev

# OpenAI (AI機能を使用する場合)
OPENAI_API_KEY=sk-your-openai-api-key
OPENAI_MODEL=gpt-4o-mini
MAX_CHAT_HISTORY=14
```

### 5. PostgreSQLの起動

```bash
make docker-start
```

これにより以下が実行されます：
- PostgreSQL 17（pgvector対応）コンテナの起動
- ポート: 5433
- データベース名: c3_app_dev
- ユーザー: c3
- パスワード: password

### 6. データベースマイグレーション

```bash
make db-update
# または
python manage.py makemigrations
python manage.py migrate
```

### 7. シードデータの投入（オプション）

```bash
python manage.py seed
```

### 8. 開発サーバーの起動

```bash
make run
# または
python manage.py runserver
```

ブラウザで http://localhost:8000 にアクセス

---

## Makeコマンド一覧

| コマンド | 説明 |
|----------|------|
| `make install` | 依存パッケージをインストール |
| `make run` | 開発サーバーを起動 |
| `make test` | テストを実行（カバレッジ付き） |
| `make lint` | Ruffでリントチェック |
| `make lint-fix` | Ruffで自動修正 |
| `make makemigrations` | マイグレーションファイル作成 |
| `make migrate` | マイグレーション実行 |
| `make db-update` | マイグレーション作成＆実行 |
| `make docker-start` | PostgreSQLコンテナ起動 |
| `make docker-stop` | PostgreSQLコンテナ停止 |
| `make docker-reset` | PostgreSQLリセット＆再構築 |
| `make docker-clean` | コンテナ・ボリューム削除 |
| `make clean` | キャッシュファイル削除 |
| `make hash TARGET=xxx` | パスワードハッシュ生成 |

---

## プロジェクト構成

```
C3/
├── c3_app/              # プロジェクト設定
│   ├── settings.py      # Django設定
│   ├── urls.py          # ルートURL
│   └── wsgi.py          # WSGI設定
│
├── accounts/            # アカウント管理
├── stores/              # 店舗管理
├── reports/             # 日報管理
├── bbs/                 # 掲示板
├── analytics/           # 分析
├── ai_features/         # AI機能
├── common/              # 共通機能
├── config/              # 管理コマンド
│
├── docs/                # ドキュメント
├── staticfiles/         # collectstatic出力先
├── media/               # アップロードファイル
│
├── requirements.txt     # 依存パッケージ
├── Makefile            # タスクランナー
├── pyproject.toml      # Ruff設定
├── render.yaml         # Renderデプロイ設定
└── manage.py           # Djangoコマンド
```

---

## Djangoアプリの構成

各アプリは以下の構成に従います：

```
app_name/
├── __init__.py
├── admin.py            # Django管理画面設定
├── apps.py             # アプリ設定
├── forms.py            # フォーム定義
├── models.py           # モデル定義
├── services.py         # ビジネスロジック
├── urls.py             # URLルーティング
├── views.py            # ビュー
├── migrations/         # マイグレーション
├── templates/          # テンプレート
│   └── app_name/
│       └── components/ # HTMXコンポーネント
├── static/             # 静的ファイル
│   └── app_name/
└── tests/              # テスト
    ├── __init__.py
    ├── test_models.py
    ├── test_views.py
    ├── test_forms.py
    └── test_services.py
```

---

## コーディング規約

### Python

- **フォーマッター/リンター**: Ruff
- **最大行長**: 120文字
- **インデント**: スペース4つ

```bash
# リントチェック
make lint

# 自動修正
make lint-fix
```

### 命名規則

| 対象 | 規則 | 例 |
|------|------|------|
| クラス | PascalCase | `DailyReport` |
| 関数/変数 | snake_case | `get_reports`, `report_id` |
| 定数 | UPPER_SNAKE_CASE | `MAX_UPLOAD_SIZE` |
| テンプレート | snake_case | `report_list.html` |
| URL名 | snake_case | `report_list` |

### Djangoビュー

```python
# 関数ベースビュー（推奨）
@login_required
def report_list(request):
    """日報一覧を表示"""
    reports = DailyReport.objects.filter(store=request.user.store)
    return render(request, 'reports/list.html', {'reports': reports})

# クラスベースビュー（API用）
class ChatView(View):
    @method_decorator(login_required)
    def post(self, request):
        """チャットメッセージを処理"""
        data = json.loads(request.body)
        # ...
        return JsonResponse({'response': response})
```

### モデル

```python
class DailyReport(models.Model):
    """日報モデル"""

    GENRE_CHOICES = [
        ('claim', 'クレーム'),
        ('praise', '賞賛'),
    ]

    report_id = models.AutoField(primary_key=True, verbose_name='日報ID')
    title = models.CharField(max_length=200, verbose_name='件名')

    class Meta:
        db_table = 'daily_reports'
        verbose_name = '日報'
        ordering = ['-date', '-created_at']

    def __str__(self):
        return f"{self.date} - {self.title}"
```

---

## テスト

### テスト実行

```bash
# 全テスト実行
make test

# 特定アプリのテスト
python manage.py test reports

# 特定テストケース
python manage.py test reports.tests.test_views.ReportViewTest

# 詳細出力
python manage.py test -v 2
```

### テストの書き方

```python
from django.test import TestCase, Client
from django.urls import reverse
from accounts.models import User
from stores.models import Store

class ReportViewTest(TestCase):
    def setUp(self):
        """テストの前準備"""
        self.store = Store.objects.create(store_name='テスト店', address='東京')
        self.user = User.objects.create_user(
            user_id='test_user',
            password='password123',
            store=self.store
        )
        self.client = Client()
        self.client.login(user_id='test_user', password='password123')

    def test_report_list_view(self):
        """日報一覧が表示されること"""
        response = self.client.get(reverse('reports:list'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'reports/list.html')
```

### カバレッジ

```bash
# カバレッジ測定
coverage run manage.py test

# レポート表示
coverage report

# HTMLレポート生成
coverage html
open htmlcov/index.html
```

---

## デバッグ

### Djangoデバッグツールバー（オプション）

```python
# settings.py
if DEBUG:
    INSTALLED_APPS += ['debug_toolbar']
    MIDDLEWARE.insert(0, 'debug_toolbar.middleware.DebugToolbarMiddleware')
```

### ログ設定

```python
# settings.py
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
        },
    },
    'root': {
        'handlers': ['console'],
        'level': 'DEBUG',
    },
}
```

### シェルでのデバッグ

```bash
python manage.py shell

>>> from reports.models import DailyReport
>>> DailyReport.objects.all()
```

---

## HTMX開発

### 基本パターン

```html
<!-- ボタンクリックで部分更新 -->
<button hx-post="/api/endpoint/"
        hx-target="#result"
        hx-swap="innerHTML">
    クリック
</button>
<div id="result"></div>
```

### Djangoビュー

```python
def api_endpoint(request):
    # 処理
    return render(request, 'components/result.html', context)
```

### HTMXレスポンスヘッダー

```python
from django.http import HttpResponse

def api_endpoint(request):
    response = render(request, 'components/result.html', context)
    response['HX-Trigger'] = 'refreshList'  # イベント発火
    return response
```

---

## AI機能開発

### ローカルでのAI機能テスト

1. `.env`に`OPENAI_API_KEY`を設定
2. 開発サーバーを起動
3. `/ai/chat/`にアクセス

### エージェントツールの追加

```python
# ai_features/tools/search_tools.py
from langchain.tools import tool

@tool
def search_daily_reports(query: str, store_id: int) -> str:
    """日報を検索します。

    Args:
        query: 検索キーワード
        store_id: 店舗ID

    Returns:
        検索結果の文字列
    """
    # 検索ロジック
    return results
```

---

## Git運用

### ブランチ戦略

```
main              # 本番環境
  └── feat/*      # 機能開発ブランチ
  └── fix/*       # バグ修正ブランチ
  └── docs/*      # ドキュメントブランチ
```

### コミットメッセージ

```
[type] 概要

詳細（必要に応じて）
```

type:
- `add`: 機能追加
- `fix`: バグ修正
- `update`: 機能改善
- `refactor`: リファクタリング
- `docs`: ドキュメント
- `test`: テスト

例：
```
[add] 日報のPDF出力機能を追加

- PDFライブラリを追加
- 出力テンプレートを作成
```

### プルリクエスト

1. 機能ブランチを作成
2. 変更をコミット
3. GitHub上でPRを作成
4. レビュー後にmainにマージ

---

## トラブルシューティング

### マイグレーションエラー

```bash
# マイグレーションをリセット
python manage.py migrate app_name zero
python manage.py makemigrations app_name
python manage.py migrate
```

### Docker PostgreSQL接続エラー

```bash
# コンテナ状態確認
docker ps

# コンテナログ確認
docker logs c3-app-postgres

# リセット
make docker-reset
```

### 静的ファイルが反映されない

```bash
python manage.py collectstatic --clear
```

---

## 関連ドキュメント

- [システムアーキテクチャ](./architecture.md)
- [APIリファレンス](./api-reference.md)
- [データベーススキーマ](./database-schema.md)
- [デプロイガイド](./deployment.md)

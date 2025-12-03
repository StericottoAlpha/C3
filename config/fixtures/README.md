# Seed Data Fixtures

このディレクトリには初期データ（seed data）のJSONファイルが格納されています。

## パスワード情報

**seed_users.json:**
- user1: password123
- user2: password123

## 使い方

`make db-reset`を実行すると、`seed_*.json`ファイルが自動的に読み込まれます。

## 新しいfixtureの追加

1. `seed_xxx.json`という名前でファイルを作成
2. Django fixture形式でデータを記述
3. パスワードを使用する場合は、このREADMEに平文を記録

### パスワードハッシュの生成方法

```bash
cd c3_app
python3 manage.py shell -c "from django.contrib.auth.hashers import make_password; print(make_password('your_password'))"
```

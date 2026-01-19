#!/usr/bin/env bash
set -o errexit

pip install -r requirements.txt

python manage.py collectstatic --no-input
python manage.py migrate --fake-initial
python manage.py create_admin_in_deploy

# デモデータセットアップ（RUN_DEMO_SETUP=true の場合のみ実行）
if [ "$RUN_DEMO_SETUP" = "true" ]; then
    echo "=== デモデータセットアップを実行します ==="
    python manage.py setup_demo_production --truncate
    echo "=== デモデータセットアップ完了 ==="
    echo "注意: RUN_DEMO_SETUP を false に変更してください（再デプロイ時のデータ重複を防ぐため）"
fi

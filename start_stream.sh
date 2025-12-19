#!/bin/bash
# ストリーミングサーバー起動スクリプト

# ポート設定（環境変数またはデフォルト）
PORT=${PORT:-8001}

echo "Starting streaming server on port $PORT..."

# uvicornでASGIアプリを起動
uvicorn asgi_stream:app \
  --host 0.0.0.0 \
  --port $PORT \
  --workers 1 \
  --timeout-keep-alive 300 \
  --log-level info

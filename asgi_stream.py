"""
ストリーミング専用ASGIアプリケーション
FastAPI + uvicorn で実行
"""
import os
import json
import logging
from typing import Optional

# Django設定を読み込む
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'c3_app.settings')

# Djangoのセットアップ
import django
django.setup()

from fastapi import FastAPI, Request, HTTPException, Depends
from fastapi.responses import StreamingResponse
from fastapi.middleware.cors import CORSMiddleware
from django.contrib.sessions.models import Session
from django.contrib.auth import get_user_model
from django.db import transaction
from datetime import datetime

from ai_features.models import AIChatHistory

logger = logging.getLogger(__name__)

app = FastAPI(title="C3 App Streaming API")

# CORS設定（必要に応じて調整）
allowed_origins = os.environ.get('ALLOWED_HOSTS', '*').split(',')
if allowed_origins and allowed_origins[0]:
    app.add_middleware(
        CORSMiddleware,
        allow_origins=[f"https://{origin}" for origin in allowed_origins if origin.strip()] +
                      [f"http://{origin}" for origin in allowed_origins if origin.strip()],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

User = get_user_model()


def get_user_from_session(request: Request):
    """
    DjangoセッションCookieからユーザーを取得
    """
    # セッションIDを取得（Djangoのデフォルトは 'sessionid'）
    session_cookie = request.cookies.get('sessionid')

    if not session_cookie:
        raise HTTPException(status_code=401, detail="認証されていません")

    try:
        # セッションを取得
        session = Session.objects.get(session_key=session_cookie)

        # セッションの有効期限チェック
        if session.expire_date < datetime.now().astimezone():
            raise HTTPException(status_code=401, detail="セッションが期限切れです")

        # セッションデータからユーザーIDを取得
        session_data = session.get_decoded()
        user_id = session_data.get('_auth_user_id')

        if not user_id:
            raise HTTPException(status_code=401, detail="認証されていません")

        # ユーザーを取得
        user = User.objects.select_related('store').get(pk=user_id)

        if not user.is_active:
            raise HTTPException(status_code=401, detail="ユーザーが無効です")

        return user

    except Session.DoesNotExist:
        raise HTTPException(status_code=401, detail="無効なセッションです")
    except User.DoesNotExist:
        raise HTTPException(status_code=401, detail="ユーザーが見つかりません")
    except Exception as e:
        logger.error(f"認証エラー: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="認証処理でエラーが発生しました")


@app.get("/")
async def root():
    """ヘルスチェック"""
    return {"status": "ok", "service": "streaming"}


@app.post("/api/ai/chat/stream/")
async def chat_stream(
    request: Request,
    user=Depends(get_user_from_session)
):
    """
    ストリーミングチャットエンドポイント
    POST /api/ai/chat/stream/

    Server-Sent Events (SSE) を使用してリアルタイムで回答を送信
    """
    try:
        # リクエストボディを取得
        body = await request.json()
        message = body.get('message', '').strip()

        if not message:
            async def error_stream():
                yield f"data: {json.dumps({'type': 'error', 'content': 'メッセージが空です'})}\n\n"
            return StreamingResponse(error_stream(), media_type='text/event-stream')

        # 環境変数からAI設定を取得
        openai_api_key = os.environ.get('OPENAI_API_KEY', '')
        openai_model = os.environ.get('OPENAI_MODEL', 'gpt-4o-mini')

        if not openai_api_key:
            async def error_stream():
                yield f"data: {json.dumps({'type': 'error', 'content': 'API KEY ERROR'})}\n\n"
            return StreamingResponse(error_stream(), media_type='text/event-stream')

        # ストリーミング生成関数
        async def event_stream():
            try:
                # Agent作成（遅延インポート）
                from ai_features.agents.chat_agent import ChatAgent

                agent = ChatAgent(
                    model_name=openai_model,
                    temperature=0.0,
                    openai_api_key=openai_api_key
                )

                # チャット履歴取得（オプション）
                chat_history = None
                if body.get('include_history', False):
                    history = AIChatHistory.objects.filter(user=user).order_by('-created_at')[:10]
                    chat_history = [
                        {
                            "role": chat.role,
                            "content": chat.message,
                        }
                        for chat in reversed(history)
                    ]

                # ステータス送信: 開始
                yield f"data: {json.dumps({'type': 'start', 'content': 'チャットを開始します...'})}\n\n"

                # エージェントからストリーミングで回答を取得
                full_response = ""
                for chunk in agent.chat_stream(
                    query=message,
                    user=user,
                    chat_history=chat_history
                ):
                    # チャンクを送信
                    yield f"data: {json.dumps({'type': 'content', 'content': chunk})}\n\n"
                    full_response += chunk

                # 完了通知
                yield f"data: {json.dumps({'type': 'done', 'content': ''})}\n\n"

                # チャット履歴を保存
                with transaction.atomic():
                    AIChatHistory.objects.create(
                        user=user,
                        role='user',
                        message=message
                    )
                    AIChatHistory.objects.create(
                        user=user,
                        role='assistant',
                        message=full_response
                    )

                    # 件数超過分を削除
                    max_chat_history = int(os.environ.get('MAX_CHAT_HISTORY', '14'))
                    qs = AIChatHistory.objects.filter(user=user).order_by('-created_at')
                    excess_count = qs.count() - max_chat_history
                    if excess_count > 0:
                        ids_to_delete = list(qs.reverse()[:excess_count].values_list('chat_id', flat=True))
                        AIChatHistory.objects.filter(chat_id__in=ids_to_delete).delete()

            except Exception as e:
                logger.error(f"Error in streaming chat: {e}", exc_info=True)
                yield f"data: {json.dumps({'type': 'error', 'content': f'エラーが発生しました: {str(e)}'})}\n\n"

        return StreamingResponse(
            event_stream(),
            media_type='text/event-stream'
        )

    except json.JSONDecodeError:
        async def error_stream():
            yield f"data: {json.dumps({'type': 'error', 'content': '無効なJSONフォーマットです'})}\n\n"
        return StreamingResponse(error_stream(), media_type='text/event-stream')
    except Exception as e:
        logger.error(f"Error in chat_stream endpoint: {e}", exc_info=True)
        async def error_stream():
            yield f"data: {json.dumps({'type': 'error', 'content': f'エラーが発生しました: {str(e)}'})}\n\n"
        return StreamingResponse(error_stream(), media_type='text/event-stream')


if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("STREAM_PORT", "8001"))
    uvicorn.run(app, host="0.0.0.0", port=port)

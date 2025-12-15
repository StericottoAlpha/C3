"""
AI Features Views
チャットエンドポイント、提案一覧、分析結果一覧など
"""
import logging
import os
import json
from typing import Dict

from django.contrib.auth.decorators import login_required
from django.http import JsonResponse, StreamingHttpResponse
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from django.views import View

from ai_features.agents import ChatAgent
from ai_features.models import AIChatHistory

logger = logging.getLogger(__name__)


class ChatView(View):
    """
    AIチャットエンドポイント
    POST /api/ai/chat/
    """

    @method_decorator(login_required)
    @method_decorator(csrf_exempt)
    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)

    def post(self, request):
        """
        チャットメッセージを処理

        Request Body:
        {
            "message": "ユーザーの質問",
            "include_history": true  // オプション: チャット履歴を含めるか
        }

        Response:
        {
            "message": "AIの回答",
            "sources": [...],
            "intermediate_steps": [...],
            "token_count": 1234
        }
        """
        try:
            import json
            data = json.loads(request.body)

            # バリデーション
            message = data.get('message', '').strip()
            if not message:
                return JsonResponse(
                    {"error": "メッセージが空です"},
                    status=400
                )

            # チャット履歴取得（オプション）
            chat_history = None
            if data.get('include_history', False):
                chat_history = self._get_chat_history(request.user)

            # 環境変数からAI設定を取得
            use_openai = os.environ.get('USE_OPENAI', 'False').lower() == 'true'
            openai_api_key = os.environ.get('OPENAI_API_KEY', '')
            openai_model = os.environ.get('OPENAI_MODEL', 'gpt-4o-mini')
            ollama_base_url = os.environ.get('OLLAMA_BASE_URL', 'http://localhost:11434')
            ollama_model = os.environ.get('OLLAMA_MODEL', 'llama3.2:3b')

            # Agentを初期化
            if use_openai:
                # OpenAI使用
                if not openai_api_key:
                    logger.warning("OPENAI_API_KEY is not set, falling back to Ollama")
                    use_openai = False
                    agent = ChatAgent(
                        model_name=ollama_model,
                        base_url=ollama_base_url,
                        temperature=0.1,
                        use_openai=False
                    )
                else:
                    agent = ChatAgent(
                        model_name=openai_model,
                        temperature=0.0,  # GPTは0.0推奨（決定論的）
                        use_openai=True,
                        openai_api_key=openai_api_key
                    )
            else:
                # Ollama使用
                agent = ChatAgent(
                    model_name=ollama_model,
                    base_url=ollama_base_url,
                    temperature=0.1,
                    use_openai=False
                )

            # チャット実行
            logger.info(f"User {request.user.username} asked: {message}")
            response = agent.chat(
                query=message,
                user=request.user,
                chat_history=chat_history
            )

            # チャット履歴をDB保存
            self._save_chat_history(
                user=request.user,
                message=message,
                response=response['message']
            )

            return JsonResponse(response)

        except json.JSONDecodeError:
            return JsonResponse(
                {"error": "無効なJSONフォーマットです"},
                status=400
            )
        except Exception as e:
            logger.error(f"Error in ChatView: {e}", exc_info=True)
            return JsonResponse(
                {"error": f"エラーが発生しました: {str(e)}"},
                status=500
            )

    def _get_chat_history(self, user, limit: int = 10) -> list:
        """
        チャット履歴を取得

        Args:
            user: ユーザーオブジェクト
            limit: 取得件数

        Returns:
            チャット履歴のリスト
        """
        history = AIChatHistory.objects.filter(user=user).order_by('-created_at')[:limit]
        return [
            {
                "role": chat.role,
                "content": chat.message,
                "created_at": chat.created_at.isoformat()
            }
            for chat in reversed(history)  # 古い順に並び替え
        ]

    def _save_chat_history(self, user, message: str, response: str):
        """
        チャット履歴をDB保存

        Args:
            user: ユーザーオブジェクト
            message: ユーザーのメッセージ
            response: AIの応答
        """
        # ユーザーメッセージを保存
        AIChatHistory.objects.create(
            user=user,
            role='user',
            message=message
        )

        # AIの応答を保存
        AIChatHistory.objects.create(
            user=user,
            role='assistant',
            message=response
        )


@login_required
@require_http_methods(["GET"])
def chat_history_view(request):
    """
    チャット履歴取得エンドポイント
    GET /api/ai/chat/history/
    """
    try:
        limit = int(request.GET.get('limit', 20))
        history = AIChatHistory.objects.filter(
            user=request.user
        ).order_by('-created_at')[:limit]

        data = [
            {
                "chat_id": chat.chat_id,
                "role": chat.role,
                "message": chat.message,
                "created_at": chat.created_at.isoformat()
            }
            for chat in reversed(history)  # 古い順に並び替え
        ]

        return JsonResponse({"history": data})

    except Exception as e:
        logger.error(f"Error in chat_history_view: {e}", exc_info=True)
        return JsonResponse(
            {"error": f"エラーが発生しました: {str(e)}"},
            status=500
        )


@login_required
@require_http_methods(["DELETE"])
@csrf_exempt
def clear_chat_history_view(request):
    """
    チャット履歴削除エンドポイント
    DELETE /api/ai/chat/history/
    """
    try:
        deleted_count = AIChatHistory.objects.filter(user=request.user).delete()[0]

        return JsonResponse({
            "message": f"{deleted_count}件のチャット履歴を削除しました"
        })

    except Exception as e:
        logger.error(f"Error in clear_chat_history_view: {e}", exc_info=True)
        return JsonResponse(
            {"error": f"エラーが発生しました: {str(e)}"},
            status=500
        )


@login_required
@require_http_methods(["GET"])
def agent_status_view(request):
    """
    Agent状態確認エンドポイント
    GET /api/ai/status/
    """
    try:
        # 環境変数から設定を取得
        use_openai = os.environ.get('USE_OPENAI', 'False').lower() == 'true'
        openai_api_key = os.environ.get('OPENAI_API_KEY', '')
        openai_model = os.environ.get('OPENAI_MODEL', 'gpt-4o-mini')
        ollama_base_url = os.environ.get('OLLAMA_BASE_URL', 'http://localhost:11434')
        ollama_model = os.environ.get('OLLAMA_MODEL', 'llama3.2:3b')

        # Ollamaの接続確認
        import requests
        ollama_status = "unknown"
        ollama_models = []
        try:
            response = requests.get(f"{ollama_base_url}/api/tags", timeout=2)
            if response.status_code == 200:
                ollama_status = "connected"
                models = response.json().get('models', [])
                ollama_models = [m.get('name') for m in models]
            else:
                ollama_status = "error"
        except Exception:
            ollama_status = "disconnected"

        # OpenAI設定状態
        openai_configured = bool(openai_api_key)

        return JsonResponse({
            "ai_mode": "openai" if use_openai else "ollama",
            "use_openai": use_openai,
            "openai_configured": openai_configured,
            "openai_model": openai_model if use_openai else None,
            "ollama_status": ollama_status,
            "ollama_base_url": ollama_base_url,
            "ollama_model": ollama_model,
            "available_ollama_models": ollama_models,
            "chat_history_count": AIChatHistory.objects.filter(user=request.user).count()
        })

    except Exception as e:
        logger.error(f"Error in agent_status_view: {e}", exc_info=True)
        return JsonResponse(
            {"error": f"エラーが発生しました: {str(e)}"},
            status=500
        )


@login_required
@require_http_methods(["POST"])
@csrf_exempt
def chat_stream_view(request):
    """
    ストリーミングチャットエンドポイント
    POST /api/ai/chat/stream/

    Server-Sent Events (SSE) を使用してリアルタイムで応答をストリーミング

    Request Body:
    {
        "message": "ユーザーの質問",
        "use_cache": true  // オプション: キャッシュを使用するか
    }

    Response: Server-Sent Events
    data: {"type": "status", "data": "処理を開始しています..."}
    data: {"type": "tool_call", "data": {...}}
    data: {"type": "tool_result", "data": {...}}
    data: {"type": "content", "data": "回答の一部"}
    data: {"type": "done", "data": {...}}
    """
    try:
        data = json.loads(request.body)

        # バリデーション
        message = data.get('message', '').strip()
        if not message:
            return JsonResponse(
                {"error": "メッセージが空です"},
                status=400
            )

        use_cache = data.get('use_cache', True)

        # 環境変数からAI設定を取得
        use_openai = os.environ.get('USE_OPENAI', 'False').lower() == 'true'
        openai_api_key = os.environ.get('OPENAI_API_KEY', '')
        openai_model = os.environ.get('OPENAI_MODEL', 'gpt-4o-mini')
        ollama_base_url = os.environ.get('OLLAMA_BASE_URL', 'http://localhost:11434')
        ollama_model = os.environ.get('OLLAMA_MODEL', 'llama3.2:3b')

        # Agentを初期化
        if use_openai and openai_api_key:
            agent = ChatAgent(
                model_name=openai_model,
                temperature=0.0,
                use_openai=True,
                openai_api_key=openai_api_key
            )
        else:
            agent = ChatAgent(
                model_name=ollama_model,
                base_url=ollama_base_url,
                temperature=0.1,
                use_openai=False
            )

        logger.info(f"User {request.user.username} asked (streaming): {message}")

        # ストリーミングジェネレータ
        def event_stream():
            """Server-Sent Events形式でストリーミング"""
            final_message = ""

            try:
                for chunk in agent.chat_stream(
                    query=message,
                    user=request.user,
                    use_tools=True,
                    use_cache=use_cache
                ):
                    # SSE形式でデータを送信
                    yield f"data: {json.dumps(chunk, ensure_ascii=False)}\n\n"

                    # 最終メッセージを記録
                    if chunk["type"] == "content":
                        final_message += chunk["data"]
                    elif chunk["type"] == "done":
                        final_message = chunk["data"].get("message", final_message)

                # チャット履歴をDB保存
                if final_message:
                    _save_chat_history_sync(
                        user=request.user,
                        message=message,
                        response=final_message
                    )

            except Exception as e:
                logger.error(f"Error in event_stream: {e}", exc_info=True)
                error_chunk = {
                    "type": "error",
                    "data": f"エラーが発生しました: {str(e)}"
                }
                yield f"data: {json.dumps(error_chunk, ensure_ascii=False)}\n\n"

        # StreamingHttpResponseを返す
        response = StreamingHttpResponse(
            event_stream(),
            content_type='text/event-stream'
        )
        response['Cache-Control'] = 'no-cache'
        response['X-Accel-Buffering'] = 'no'  # nginxのバッファリング無効化
        return response

    except json.JSONDecodeError:
        return JsonResponse(
            {"error": "無効なJSONフォーマットです"},
            status=400
        )
    except Exception as e:
        logger.error(f"Error in chat_stream_view: {e}", exc_info=True)
        return JsonResponse(
            {"error": f"エラーが発生しました: {str(e)}"},
            status=500
        )


def _save_chat_history_sync(user, message: str, response: str):
    """
    チャット履歴をDB保存（同期版）

    Args:
        user: ユーザーオブジェクト
        message: ユーザーのメッセージ
        response: AIの応答
    """
    try:
        # ユーザーメッセージを保存
        AIChatHistory.objects.create(
            user=user,
            role='user',
            message=message
        )

        # AIの応答を保存
        AIChatHistory.objects.create(
            user=user,
            role='assistant',
            message=response
        )
    except Exception as e:
        logger.error(f"Error saving chat history: {e}", exc_info=True)


class ChatParallelView(View):
    """
    並列ツール実行対応のAIチャットエンドポイント
    POST /api/ai/chat/parallel/

    複数のツールが呼ばれた場合、並列実行して高速化
    """

    @method_decorator(login_required)
    @method_decorator(csrf_exempt)
    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)

    def post(self, request):
        """
        チャットメッセージを処理（並列ツール実行）

        Request Body:
        {
            "message": "ユーザーの質問",
            "include_history": true  // オプション: チャット履歴を含めるか
        }

        Response:
        {
            "message": "AIの回答",
            "sources": [...],
            "intermediate_steps": [...],
            "token_count": 1234,
            "parallel_execution": true
        }
        """
        try:
            data = json.loads(request.body)

            # バリデーション
            message = data.get('message', '').strip()
            if not message:
                return JsonResponse(
                    {"error": "メッセージが空です"},
                    status=400
                )

            # チャット履歴取得（オプション）
            chat_history = None
            if data.get('include_history', False):
                # 既存のChatViewのメソッドを使用できないので、ここで実装
                history = AIChatHistory.objects.filter(
                    user=request.user
                ).order_by('-created_at')[:10]
                chat_history = [
                    {
                        "role": chat.role,
                        "content": chat.message,
                        "created_at": chat.created_at.isoformat()
                    }
                    for chat in reversed(history)
                ]

            # 環境変数からAI設定を取得
            use_openai = os.environ.get('USE_OPENAI', 'False').lower() == 'true'
            openai_api_key = os.environ.get('OPENAI_API_KEY', '')
            openai_model = os.environ.get('OPENAI_MODEL', 'gpt-4o-mini')
            ollama_base_url = os.environ.get('OLLAMA_BASE_URL', 'http://localhost:11434')
            ollama_model = os.environ.get('OLLAMA_MODEL', 'llama3.2:3b')

            # Agentを初期化
            if use_openai:
                if not openai_api_key:
                    logger.warning("OPENAI_API_KEY is not set, falling back to Ollama")
                    use_openai = False
                    agent = ChatAgent(
                        model_name=ollama_model,
                        base_url=ollama_base_url,
                        temperature=0.1,
                        use_openai=False
                    )
                else:
                    agent = ChatAgent(
                        model_name=openai_model,
                        temperature=0.0,
                        use_openai=True,
                        openai_api_key=openai_api_key
                    )
            else:
                agent = ChatAgent(
                    model_name=ollama_model,
                    base_url=ollama_base_url,
                    temperature=0.1,
                    use_openai=False
                )

            # チャット実行（並列モード）
            logger.info(f"User {request.user.username} asked (parallel): {message}")

            # ユーザー情報を収集
            user_name = getattr(request.user, 'email', getattr(request.user, 'user_id', '不明'))
            store_id = request.user.store.store_id if hasattr(request.user, 'store') and request.user.store else None
            store_name = request.user.store.store_name if hasattr(request.user, 'store') and request.user.store else "不明"

            from datetime import datetime as dt

            system_info = f"""You are a restaurant operations support AI assistant. You help store managers and staff by retrieving accurate information from the database.

## Current Context
- Date/Time: {dt.now().strftime("%Y-%m-%d %H:%M:%S")}
- User: {user_name}
- Store: {store_name} (ID: {store_id or "Unknown"})

## Critical Rules
1. **ALWAYS use tools**: You have NO knowledge about this restaurant's data. You MUST use tools to retrieve ALL information.
2. **NEVER guess or assume**: Base your answers ONLY on actual data retrieved from tools.
3. **Be honest**: If no data is found after using tools, say "No data available" in Japanese.

## Response Style
- Respond in Japanese (日本語で回答)
- Be concise and use bullet points
- Include specific numbers from tool results
- State conclusions first"""

            if store_id:
                tools = agent._create_tools_for_store(store_id)
                response_text, intermediate_steps = agent._react_loop_parallel(
                    query=message,
                    tools=tools,
                    system_info=system_info,
                    max_iterations=5
                )
            else:
                response_text = "店舗情報が見つかりません。"
                intermediate_steps = []

            # 結果を整形
            response = {
                "message": response_text,
                "sources": [],
                "intermediate_steps": intermediate_steps,
                "token_count": agent._estimate_tokens(response_text),
                "parallel_execution": True
            }

            # チャット履歴をDB保存
            _save_chat_history_sync(
                user=request.user,
                message=message,
                response=response['message']
            )

            return JsonResponse(response)

        except json.JSONDecodeError:
            return JsonResponse(
                {"error": "無効なJSONフォーマットです"},
                status=400
            )
        except Exception as e:
            logger.error(f"Error in ChatParallelView: {e}", exc_info=True)
            return JsonResponse(
                {"error": f"エラーが発生しました: {str(e)}"},
                status=500
            )

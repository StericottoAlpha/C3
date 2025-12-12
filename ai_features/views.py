"""
AI Features Views
チャットエンドポイント、提案一覧、分析結果一覧など
"""
import logging
from typing import Dict

from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
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

            # Agentを初期化
            agent = ChatAgent(
                model_name="llama3.2:3b",
                base_url="http://localhost:11434",
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
        # Ollamaの接続確認
        import requests
        ollama_status = "unknown"
        try:
            response = requests.get("http://localhost:11434/api/tags", timeout=2)
            if response.status_code == 200:
                ollama_status = "connected"
                models = response.json().get('models', [])
                model_names = [m.get('name') for m in models]
            else:
                ollama_status = "error"
                model_names = []
        except Exception:
            ollama_status = "disconnected"
            model_names = []

        return JsonResponse({
            "ollama_status": ollama_status,
            "available_models": model_names,
            "default_model": "llama3.2:3b",
            "chat_history_count": AIChatHistory.objects.filter(user=request.user).count()
        })

    except Exception as e:
        logger.error(f"Error in agent_status_view: {e}", exc_info=True)
        return JsonResponse(
            {"error": f"エラーが発生しました: {str(e)}"},
            status=500
        )

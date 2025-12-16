import logging
import os
import json
from typing import Dict

from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse, StreamingHttpResponse
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from django.views import View

from ai_features.agents.chat_agent import ChatAgent
from ai_features.models import AIChatHistory

@login_required
def chat_page_view(request):

    if request.method == "POST":
        pass

    elif request.method == "GET":

        context = {
            "username": request.user.first_name,
        }
        return render(request, "ai_features/chat.html", context)


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
            openai_api_key = os.environ.get('OPENAI_API_KEY', '')
            openai_model = os.environ.get('OPENAI_MODEL', 'gpt-4o-mini')

            # Agentを初期化
            if openai_api_key:
                agent = ChatAgent(
                    model_name=openai_model,
                    temperature=0.0,  # GPTは0.0推奨（決定論的）
                    use_openai=True,
                    openai_api_key=openai_api_key
                )
                
            else:
                return JsonResponse(
                    {"error": "API KEY ERROR"},
                    status = 401
                )


            # チャット実行
            # logger.info(f"User {request.user.username} asked: {message}")
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

    def get(self, request):

        chat_history = self._get_chat_history(request.user, 20)
        return JsonResponse(
            {"history": chat_history},
            status = 200
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
        チャット履歴をDB保存（MAX_CHAT_HISTORY件数まで）

        Args:
            user: ユーザーオブジェクト
            message: ユーザーのメッセージ
            response: AIの応答
        """

        max_chat_history = os.environ.get('MAX_CHAT_HISTORY', 14)

        with transaction.atomic():
            # ユーザー発言
            AIChatHistory.objects.create(
                user=user,
                role='user',
                message=message
            )

            # AI応答
            AIChatHistory.objects.create(
                user=user,
                role='assistant',
                message=response
            )

            # 件数超過分を削除（古い順）
            qs = AIChatHistory.objects.filter(user=user).order_by('-created_at')

            excess_count = qs.count() - max_chat_history
            if excess_count > 0:
                qs.reverse()[:excess_count].delete()


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
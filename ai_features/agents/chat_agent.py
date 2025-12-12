"""
LangChain Chat Agent
Ollama/OpenAI を使用した会話型AI
"""
import logging
from typing import List, Dict, Optional
from datetime import datetime

from langchain_community.llms import Ollama

logger = logging.getLogger(__name__)


class ChatAgent:
    """
    LangChain Chat Agent
    Ollama (実験) または OpenAI API (本番) を使用
    """

    # システムプロンプト
    SYSTEM_PROMPT = """あなたはレストラン運営支援AIアシスタントです。
店舗の日報、掲示板、実績データ、マニュアルから情報を検索し、店舗運営をサポートします。

【現在の情報】
日時: {current_datetime}
ユーザー: {user_name}
店舗ID: {store_id}
店舗名: {store_name}

ユーザーの質問に簡潔に答えてください。

質問: {query}"""

    def __init__(
        self,
        model_name: str = "llama3.2:3b",
        base_url: str = "http://localhost:11434",
        temperature: float = 0.1,
        use_openai: bool = False,
        openai_api_key: Optional[str] = None
    ):
        """
        Args:
            model_name: モデル名（Ollama: "llama3.2:3b", OpenAI: "gpt-4o-mini"）
            base_url: Ollama APIのURL
            temperature: 温度パラメータ（0.0-1.0）
            use_openai: OpenAI APIを使用する場合True
            openai_api_key: OpenAI APIキー
        """
        self.model_name = model_name
        self.base_url = base_url
        self.temperature = temperature
        self.use_openai = use_openai
        self.openai_api_key = openai_api_key

        # LLMの初期化
        self.llm = self._initialize_llm()

    def _initialize_llm(self):
        """LLMを初期化"""
        if self.use_openai:
            # OpenAI API使用（本番環境）
            from langchain_openai import ChatOpenAI
            return ChatOpenAI(
                model=self.model_name,
                temperature=self.temperature,
                api_key=self.openai_api_key
            )
        else:
            # Ollama使用（実験環境）
            return Ollama(
                model=self.model_name,
                base_url=self.base_url,
                temperature=self.temperature
            )

    def chat(
        self,
        query: str,
        user,
        chat_history: Optional[List[Dict]] = None
    ) -> Dict:
        """
        チャット実行

        Args:
            query: ユーザーの質問
            user: Djangoユーザーオブジェクト
            chat_history: チャット履歴（オプション）

        Returns:
            {
                "message": "回答テキスト",
                "sources": [],
                "intermediate_steps": [],
                "token_count": 推定値
            }
        """
        try:
            # ユーザー情報を収集
            user_name = getattr(user, 'email', getattr(user, 'user_id', '不明'))
            user_info = {
                "current_datetime": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "user_name": user_name,
                "store_id": user.store.store_id if hasattr(user, 'store') and user.store else "不明",
                "store_name": user.store.store_name if hasattr(user, 'store') and user.store else "不明",
                "query": query
            }

            # プロンプト構築
            prompt = self.SYSTEM_PROMPT.format(**user_info)

            # LLM呼び出し
            logger.info(f"Invoking LLM with query: {query}")
            response_text = self.llm.invoke(prompt)

            # 結果を整形
            response = {
                "message": response_text,
                "sources": [],
                "intermediate_steps": [],
                "token_count": self._estimate_tokens(response_text),
            }

            return response

        except Exception as e:
            logger.error(f"Error in chat: {e}", exc_info=True)
            return {
                "message": f"エラーが発生しました: {str(e)}",
                "sources": [],
                "intermediate_steps": [],
                "token_count": 0,
            }

    def _estimate_tokens(self, text: str) -> int:
        """トークン数を推定"""
        # 簡易的な推定（実際はtiktokenなどを使用）
        return len(str(text)) // 4  # 4文字 ≈ 1トークン（おおよそ）

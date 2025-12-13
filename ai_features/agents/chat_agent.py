"""
LangChain Chat Agent with ReAct
Ollama/OpenAI を使用した会話型AI（LangChain公式ReActエージェント版）
"""
import logging
from typing import List, Dict, Optional
from datetime import datetime
import re

from langchain_community.llms import Ollama
from langchain_community.chat_models import ChatOllama
from langchain_experimental.llms.ollama_functions import OllamaFunctions
from langchain_core.tools import tool
from langgraph.prebuilt import create_react_agent

logger = logging.getLogger(__name__)


class ChatAgent:
    """
    LangChain Chat Agent with ReAct
    Ollama (実験) または OpenAI API (本番) を使用
    """

    def __init__(
        self,
        model_name: str = "llama3.1:latest",
        base_url: str = "http://localhost:11434",
        temperature: float = 0.1,
        use_openai: bool = False,
        openai_api_key: Optional[str] = None
    ):
        """
        Args:
            model_name: モデル名（Ollama: "llama3.1:latest", OpenAI: "gpt-4o-mini"）
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
        """LLMを初期化（ツールコーリング対応モデル）"""
        if self.use_openai:
            # OpenAI API使用（本番環境）- ネイティブツールコーリングサポート
            from langchain_openai import ChatOpenAI
            return ChatOpenAI(
                model=self.model_name,
                temperature=self.temperature,
                api_key=self.openai_api_key
            )
        else:
            # Ollama使用（実験環境）- OllamaFunctionsでツールコーリングをエミュレート
            return OllamaFunctions(
                model=self.model_name,
                base_url=self.base_url,
                temperature=self.temperature,
                format="json"  # JSON出力を強制
            )

    def _create_tools_for_store(self, store_id: int) -> List:
        """
        store_idをバインドしたツールリストを作成

        Args:
            store_id: 店舗ID

        Returns:
            ツールのリスト
        """
        from ai_features.tools.search_tools import (
            search_daily_reports as _search_daily_reports,
            search_bbs_posts as _search_bbs_posts,
            search_manual
        )
        from ai_features.tools.analytics_tools import (
            get_claim_statistics as _get_claim_statistics,
            get_sales_trend as _get_sales_trend,
            get_cash_difference_analysis as _get_cash_difference_analysis
        )

        # store_idをクロージャでキャプチャしたツール関数を作成
        @tool
        def search_daily_reports(query: str, days: int = 30) -> str:
            """日報データを検索します。クレーム、賞賛、事故、設備トラブル、報告内容などを検索する際に使用してください。キーワード例: 「クレーム」「褒められた」「事故」「トラブル」「接客」「提供」"""
            return _search_daily_reports.invoke({"query": query, "store_id": store_id, "days": days})

        @tool
        def search_bbs_posts(query: str, days: int = 30) -> str:
            """掲示板の投稿とコメントを検索します。店舗内の議論、意見交換、コミュニケーション履歴を確認する際に使用してください。キーワード例: 「議論」「投稿」「コメント」「意見」"""
            return _search_bbs_posts.invoke({"query": query, "store_id": store_id, "days": days})

        @tool
        def get_claim_statistics(days: int = 30) -> str:
            """クレーム統計を取得します。クレームの件数、発生率、傾向、カテゴリ別集計など統計情報が必要な際に使用してください。キーワード例: 「件数」「統計」「傾向」「分析」"""
            return _get_claim_statistics.invoke({"store_id": store_id, "days": days})

        @tool
        def get_sales_trend(days: int = 30) -> str:
            """売上推移データを取得します。売上の合計、平均、トレンド（上昇/下降/安定）、週別推移など売上分析が必要な際に使用してください。キーワード例: 「売上」「推移」「トレンド」"""
            return _get_sales_trend.invoke({"store_id": store_id, "days": days})

        @tool
        def get_cash_difference_analysis(days: int = 30) -> str:
            """現金過不足分析データを取得します。違算金額、発生件数、プラス/マイナスの内訳など現金管理の分析が必要な際に使用してください。キーワード例: 「過不足」「違算」「現金」"""
            return _get_cash_difference_analysis.invoke({"store_id": store_id, "days": days})

        tools = [
            search_daily_reports,
            search_bbs_posts,
            search_manual,  # store_id不要なのでそのまま
            get_claim_statistics,
            get_sales_trend,
            get_cash_difference_analysis,
        ]

        return tools

    def chat(
        self,
        query: str,
        user,
        chat_history: Optional[List[Dict]] = None,
        use_tools: bool = True
    ) -> Dict:
        """
        チャット実行

        Args:
            query: ユーザーの質問
            user: Djangoユーザーオブジェクト
            chat_history: チャット履歴（オプション）
            use_tools: ツールを使用するか（デフォルト: True）

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
            store_id = user.store.store_id if hasattr(user, 'store') and user.store else None
            store_name = user.store.store_name if hasattr(user, 'store') and user.store else "不明"

            # システムプロンプト
            system_info = f"""あなたはレストラン運営支援AIアシスタントです。

【現在の情報】
日時: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}
ユーザー: {user_name}
店舗ID: {store_id or "不明"}
店舗名: {store_name}

【重要なルール】
1. **必ずツールを使用してデータを取得してから回答してください**
2. 自分の知識や推測だけで回答してはいけません
3. 質問に関連するツールが存在する場合、必ず実行してから回答してください
4. 実データに基づいた具体的で正確な回答を心がけてください

【ツール選択のガイド】
- クレーム、賞賛、事故、日報の内容を検索 → search_daily_reports
- 掲示板の議論や投稿を検索 → search_bbs_posts
- 業務マニュアル、手順書を検索 → search_manual
- クレームの件数、傾向、統計 → get_claim_statistics
- 売上の推移、トレンド、分析 → get_sales_trend
- 現金過不足、違算の分析 → get_cash_difference_analysis

簡潔で分かりやすい日本語で回答してください。"""

            # ツールを使用する場合（ReActエージェント）
            if use_tools and store_id:
                logger.info(f"Creating ReAct agent for store_id={store_id}")

                # ツール作成
                tools = self._create_tools_for_store(store_id)

                # ReActループの実装
                response_text, intermediate_steps = self._react_loop(
                    query=query,
                    tools=tools,
                    system_info=system_info,
                    max_iterations=5
                )

            else:
                # ツールなしで直接LLM呼び出し
                logger.info(f"Invoking LLM without tools")
                prompt = f"{system_info}\n\n質問: {query}"
                response_text = self.llm.invoke(prompt)
                intermediate_steps = []

            # 結果を整形
            response = {
                "message": response_text,
                "sources": [],
                "intermediate_steps": intermediate_steps,
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

    def _react_loop(
        self,
        query: str,
        tools: List,
        system_info: str,
        max_iterations: int = 5
    ) -> tuple[str, List[Dict]]:
        """
        LangGraph ReActエージェントを使用した実装（最新）

        Args:
            query: ユーザーの質問
            tools: 利用可能なツールリスト
            system_info: システムプロンプト
            max_iterations: 最大反復回数

        Returns:
            (最終回答, 中間ステップリスト)
        """
        try:
            # システムプロンプトを作成
            system_prompt = f"""{system_info}

IMPORTANT: Respond to the user's question in Japanese. Use the tools to gather information, then provide a clear answer in Japanese."""

            # LangGraph ReActエージェントを作成（最新の推奨方法）
            agent_executor = create_react_agent(
                model=self.llm,
                tools=tools,
                prompt=system_prompt
            )

            # エージェント実行
            result = agent_executor.invoke({
                "messages": [("user", query)]
            })

            # 結果を取得（LangGraphの出力形式）
            messages = result.get("messages", [])

            # 最後のメッセージから回答を取得
            final_message = ""
            if messages:
                last_message = messages[-1]
                if hasattr(last_message, 'content'):
                    final_message = last_message.content
                else:
                    final_message = str(last_message)

            # 中間ステップを抽出
            intermediate_steps = []
            for msg in messages:
                # ツール呼び出しメッセージをチェック
                if hasattr(msg, 'additional_kwargs'):
                    tool_calls = msg.additional_kwargs.get('tool_calls', [])
                    for tool_call in tool_calls:
                        intermediate_steps.append({
                            "thought": "",
                            "action": tool_call.get('function', {}).get('name', ''),
                            "action_input": tool_call.get('function', {}).get('arguments', ''),
                            "observation": ""
                        })

            return final_message, intermediate_steps

        except Exception as e:
            logger.error(f"Agent execution error: {e}", exc_info=True)
            import traceback
            traceback.print_exc()

            # エラー時は直接LLMで回答を生成
            fallback_prompt = f"{system_info}\n\n質問: {query}\n\n回答:"
            fallback_response = self.llm.invoke(fallback_prompt)
            return fallback_response, []

    def _estimate_tokens(self, text: str) -> int:
        """トークン数を推定"""
        return len(str(text)) // 4

import hashlib
import json
import asyncio
from typing import List, Dict, Optional, Iterator
from datetime import datetime, timedelta
from functools import lru_cache

from langchain_core.tools import tool
from langgraph.prebuilt import create_react_agent
from langchain_openai import ChatOpenAI

# シンプルなメモリキャッシュ（TTL付き）
_cache = {}
_cache_timestamps = {}


class ChatAgent:
    """
    LangChain ReAct Chat Agent
    """

    def __init__(
        self,
        model_name: str = "gpt-4o-mini",
        temperature: float = 0.0,
        openai_api_key: Optional[str] = None,
    ):
        """
        Args:
            model_name: OpenAIモデル名（デフォルト: "gpt-4o-mini"）
            temperature: 温度パラメータ（0.0-1.0、推奨: 0.0-0.2）
            openai_api_key: OpenAI APIキー
        """
        self.model_name = model_name
        self.temperature = temperature
        self.openai_api_key = openai_api_key

        # LLMの初期化
        self.llm = self._initialize_llm()

        # ストリーミング用LLMの初期化
        self.llm_streaming = self._initialize_llm_streaming()

    def _initialize_llm_streaming(self):
        """ストリーミング用LLMを初期化"""

        llm = ChatOpenAI(
            model=self.model_name,
            temperature=self.temperature,
            api_key=self.openai_api_key,
            streaming=True  # ストリーミング有効化
        )
        return llm


    def _initialize_llm(self):
        """LLMを初期化"""

        llm = ChatOpenAI(
            model=self.model_name,
            temperature=self.temperature,
            api_key=self.openai_api_key
        )
        return llm

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

        # Create tool functions with store_id bound via closure
        @tool
        def search_daily_reports(query: str, days: int = 30) -> str:
            """
            Search daily reports database for claims, compliments, accidents, and report contents.

            When to use this tool:
            - When investigating specific incidents like claims (クレーム), compliments (賞賛), accidents (事故), troubles
            - When searching with time periods like "last week" (先週), "this month" (今月)
            - When searching by category like customer service (接客), food service (提供)

            Args:
                query: Search keyword (e.g., "クレーム", "接客", "提供時間")
                days: Search period in days (default: 30)
            """
            return _search_daily_reports.invoke({"query": query, "store_id": store_id, "days": days})

        @tool
        def search_bbs_posts(query: str, days: int = 30) -> str:
            """
            Search bulletin board posts and comments for discussions and opinions among staff.

            When to use this tool:
            - When checking discussions or opinions among staff members
            - When searching for posts about specific topics

            Args:
                query: Search keyword (e.g., "シフト", "メニュー改善")
                days: Search period in days (default: 30)
            """
            return _search_bbs_posts.invoke({"query": query, "store_id": store_id, "days": days})

        @tool
        def get_claim_statistics(days: int = 30) -> str:
            """
            Get claim statistics (count, trends, breakdown by category).

            When to use this tool:
            - When you need total number of claims or occurrence rate
            - When trend analysis of claims is needed
            - When numerical information is requested like "how many" (何件), "how much" (どのくらい)

            Args:
                days: Aggregation period in days (default: 30)
            """
            return _get_claim_statistics.invoke({"store_id": store_id, "days": days})

        @tool
        def get_sales_trend(days: int = 30) -> str:
            """
            Get sales trend data (total, average, trend, weekly breakdown).

            When to use this tool:
            - When checking sales trends or patterns
            - When comparison with previous week/month is needed
            - When checking sales goal achievement status

            Args:
                days: Aggregation period in days (default: 30)
            """
            return _get_sales_trend.invoke({"store_id": store_id, "days": days})

        @tool
        def get_cash_difference_analysis(days: int = 30) -> str:
            """
            Get cash difference analysis data (amount, count, plus/minus breakdown).

            When to use this tool:
            - When checking cash register discrepancy status
            - When analyzing cash management issues

            Args:
                days: Aggregation period in days (default: 30)
            """
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

            # System prompt (English, ReAct-optimized)
            system_info = f"""You are a restaurant operations support AI assistant. You help store managers and staff by retrieving accurate information from the database.

## Current Context
- Date/Time: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}
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
            # Manual ReAct implementation with tool binding
            from langchain_core.messages import SystemMessage, HumanMessage, ToolMessage

            # System message with tool usage guidance
            system_message = SystemMessage(content=f"""{system_info}

CRITICAL: You do NOT have any prior knowledge about this restaurant's data.
You MUST use the provided tools to answer ALL questions about claims, sales, reports, etc.

For the question "先週のクレーム", you MUST call search_daily_reports tool with query="クレーム" and days=7.

Always respond in Japanese after retrieving data from tools.""")

            # Bind tools to the LLM
            llm_with_tools = self.llm.bind_tools(tools)

            # Create messages
            messages = [system_message, HumanMessage(content=query)]

            # Invoke LLM with tools
            logger.info(f"Invoking LLM with tools for query: {query}")
            response = llm_with_tools.invoke(messages)

            intermediate_steps = []

            # Check if tools were called
            if hasattr(response, 'tool_calls') and response.tool_calls:
                logger.info(f"Tools called: {len(response.tool_calls)}")

                # Execute tool calls
                tool_results = []
                for tool_call in response.tool_calls:
                    tool_name = tool_call['name']
                    tool_args = tool_call['args']
                    logger.info(f"Executing tool: {tool_name} with args: {tool_args}")

                    # Find and execute the tool
                    for tool in tools:
                        if tool.name == tool_name:
                            result_text = tool.invoke(tool_args)
                            tool_results.append(ToolMessage(
                                content=str(result_text),
                                tool_call_id=tool_call['id']
                            ))

                            intermediate_steps.append({
                                "thought": "",
                                "action": tool_name,
                                "action_input": str(tool_args),
                                "observation": str(result_text)
                            })
                            break

                # Get final response with tool results
                messages.append(response)
                messages.extend(tool_results)

                final_response = llm_with_tools.invoke(messages)
                final_message = final_response.content if hasattr(final_response, 'content') else str(final_response)
            else:
                logger.warning("No tools were called")
                final_message = response.content if hasattr(response, 'content') else str(response)

            return final_message, intermediate_steps

        except Exception as e:
            logger.error(f"Agent execution error: {e}", exc_info=True)
            import traceback
            traceback.print_exc()

            # エラー時は直接LLMで回答を生成
            fallback_prompt = f"{system_info}\n\n質問: {query}\n\n回答:"
            fallback_response = self.llm.invoke(fallback_prompt)
            # AIMessageの場合、contentを取得
            if hasattr(fallback_response, 'content'):
                fallback_text = fallback_response.content if isinstance(fallback_response.content, str) else str(fallback_response.content)
            else:
                fallback_text = str(fallback_response)
            return fallback_text, []

    def _estimate_tokens(self, text: str) -> int:
        """トークン数を推定"""
        return len(str(text)) // 4

    async def _execute_tools_parallel(self, tool_calls: List, tools: List) -> tuple[List, List[Dict]]:
        """
        ツールを並列実行

        Args:
            tool_calls: ツール呼び出しのリスト
            tools: 利用可能なツールのリスト

        Returns:
            (ToolMessageのリスト, intermediate_stepsのリスト)
        """
        from langchain_core.messages import ToolMessage
        import concurrent.futures

        tool_results = []
        intermediate_steps = []

        # 並列実行用のタスクリスト
        tasks = []
        for tool_call in tool_calls:
            tool_name = tool_call['name']
            tool_args = tool_call['args']
            tool_id = tool_call['id']

            # 該当するツールを探す
            for tool in tools:
                if tool.name == tool_name:
                    tasks.append((tool, tool_name, tool_args, tool_id))
                    break

        # ThreadPoolExecutorで並列実行
        with concurrent.futures.ThreadPoolExecutor(max_workers=len(tasks)) as executor:
            # 各ツールを並列実行
            future_to_task = {
                executor.submit(task[0].invoke, task[2]): task
                for task in tasks
            }

            for future in concurrent.futures.as_completed(future_to_task):
                task = future_to_task[future]
                tool, tool_name, tool_args, tool_id = task

                try:
                    result_text = future.result()
                    tool_results.append(ToolMessage(
                        content=str(result_text),
                        tool_call_id=tool_id
                    ))

                    intermediate_steps.append({
                        "thought": "",
                        "action": tool_name,
                        "action_input": str(tool_args),
                        "observation": str(result_text)
                    })

                    logger.info(f"Tool completed (parallel): {tool_name}")

                except Exception as e:
                    logger.error(f"Error executing tool {tool_name}: {e}")
                    # エラーでも続行
                    tool_results.append(ToolMessage(
                        content=f"Error: {str(e)}",
                        tool_call_id=tool_id
                    ))

        return tool_results, intermediate_steps

    def _react_loop_parallel(
        self,
        query: str,
        tools: List,
        system_info: str,
        max_iterations: int = 5
    ) -> tuple[str, List[Dict]]:
        """
        並列ツール実行対応のReActループ

        Args:
            query: ユーザーの質問
            tools: 利用可能なツールリスト
            system_info: システムプロンプト
            max_iterations: 最大反復回数

        Returns:
            (最終回答, 中間ステップリスト)
        """
        try:
            from langchain_core.messages import SystemMessage, HumanMessage, ToolMessage

            # System message
            system_message = SystemMessage(content=f"""{system_info}

CRITICAL: You do NOT have any prior knowledge about this restaurant's data.
You MUST use the provided tools to answer ALL questions about claims, sales, reports, etc.

For the question "先週のクレーム", you MUST call search_daily_reports tool with query="クレーム" and days=7.

Always respond in Japanese after retrieving data from tools.""")

            # Bind tools to LLM
            llm_with_tools = self.llm.bind_tools(tools)

            # Create messages
            messages = [system_message, HumanMessage(content=query)]

            # Invoke LLM with tools
            logger.info(f"Invoking LLM with tools (parallel mode) for query: {query}")
            response = llm_with_tools.invoke(messages)

            intermediate_steps = []

            # Check if tools were called
            if hasattr(response, 'tool_calls') and response.tool_calls:
                num_tools = len(response.tool_calls)
                logger.info(f"Tools called: {num_tools}")

                if num_tools > 1:
                    # 並列実行（複数ツール）
                    logger.info(f"Executing {num_tools} tools in PARALLEL")
                    tool_results, intermediate_steps = asyncio.run(
                        self._execute_tools_parallel(response.tool_calls, tools)
                    )
                else:
                    # 単一ツールの場合は通常実行
                    tool_results = []
                    for tool_call in response.tool_calls:
                        tool_name = tool_call['name']
                        tool_args = tool_call['args']
                        logger.info(f"Executing single tool: {tool_name}")

                        for tool in tools:
                            if tool.name == tool_name:
                                result_text = tool.invoke(tool_args)
                                tool_results.append(ToolMessage(
                                    content=str(result_text),
                                    tool_call_id=tool_call['id']
                                ))

                                intermediate_steps.append({
                                    "thought": "",
                                    "action": tool_name,
                                    "action_input": str(tool_args),
                                    "observation": str(result_text)
                                })
                                break

                # Get final response with tool results
                messages.append(response)
                messages.extend(tool_results)

                final_response = llm_with_tools.invoke(messages)
                final_message = final_response.content if hasattr(final_response, 'content') else str(final_response)
            else:
                logger.warning("No tools were called")
                final_message = response.content if hasattr(response, 'content') else str(response)

            return final_message, intermediate_steps

        except Exception as e:
            logger.error(f"Agent execution error (parallel): {e}", exc_info=True)
            import traceback
            traceback.print_exc()

            # エラー時は直接LLMで回答を生成
            fallback_prompt = f"{system_info}\n\n質問: {query}\n\n回答:"
            fallback_response = self.llm.invoke(fallback_prompt)
            if hasattr(fallback_response, 'content'):
                fallback_text = fallback_response.content if isinstance(fallback_response.content, str) else str(fallback_response.content)
            else:
                fallback_text = str(fallback_response)
            return fallback_text, []

    @staticmethod
    def _generate_cache_key(query: str, store_id: int, days: int = None) -> str:
        """キャッシュキーを生成"""
        key_data = f"{query}_{store_id}_{days if days else 'default'}"
        return hashlib.md5(key_data.encode()).hexdigest()

    @staticmethod
    def _get_from_cache(cache_key: str, ttl_seconds: int = 3600) -> Optional[str]:
        """キャッシュから取得（TTLチェック付き）"""
        global _cache, _cache_timestamps

        if cache_key in _cache:
            timestamp = _cache_timestamps.get(cache_key)
            if timestamp and datetime.now() - timestamp < timedelta(seconds=ttl_seconds):
                logger.info(f"Cache hit: {cache_key}")
                return _cache[cache_key]
            else:
                # 期限切れキャッシュを削除
                del _cache[cache_key]
                del _cache_timestamps[cache_key]
                logger.info(f"Cache expired: {cache_key}")

        return None

    @staticmethod
    def _set_to_cache(cache_key: str, value: str):
        """キャッシュに保存"""
        global _cache, _cache_timestamps
        _cache[cache_key] = value
        _cache_timestamps[cache_key] = datetime.now()
        logger.info(f"Cache set: {cache_key}")

    def chat_stream(
        self,
        query: str,
        user,
        chat_history: Optional[List[Dict]] = None,
        use_tools: bool = True,
        use_cache: bool = True
    ) -> Iterator[Dict]:
        """
        ストリーミング対応のチャット実行

        Args:
            query: ユーザーの質問
            user: Djangoユーザーオブジェクト
            chat_history: チャット履歴（オプション）
            use_tools: ツールを使用するか（デフォルト: True）
            use_cache: キャッシュを使用するか（デフォルト: True）

        Yields:
            {
                "type": "status" | "tool_call" | "tool_result" | "content" | "done",
                "data": データ内容
            }
        """
        try:
            # ユーザー情報を収集
            user_name = getattr(user, 'email', getattr(user, 'user_id', '不明'))
            store_id = user.store.store_id if hasattr(user, 'store') and user.store else None
            store_name = user.store.store_name if hasattr(user, 'store') and user.store else "不明"

            yield {"type": "status", "data": "処理を開始しています..."}

            # キャッシュチェック
            if use_cache and store_id:
                cache_key = self._generate_cache_key(query, store_id)
                cached_result = self._get_from_cache(cache_key, ttl_seconds=3600)  # 1時間キャッシュ

                if cached_result:
                    yield {"type": "status", "data": "キャッシュから回答を取得しました"}
                    yield {"type": "content", "data": cached_result}
                    yield {
                        "type": "done",
                        "data": {
                            "message": cached_result,
                            "from_cache": True,
                            "intermediate_steps": []
                        }
                    }
                    return

            # System prompt
            system_info = f"""You are a restaurant operations support AI assistant. You help store managers and staff by retrieving accurate information from the database.

## Current Context
- Date/Time: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}
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

            # ツールを使用する場合
            if use_tools and store_id:
                yield {"type": "status", "data": "ツールを準備しています..."}

                tools = self._create_tools_for_store(store_id)

                # ストリーミング版のReActループ
                final_message = ""
                intermediate_steps = []

                for chunk in self._react_loop_stream(query, tools, system_info):
                    if chunk["type"] == "tool_call":
                        yield {"type": "tool_call", "data": chunk["data"]}
                    elif chunk["type"] == "tool_result":
                        yield {"type": "tool_result", "data": chunk["data"]}
                        intermediate_steps.append(chunk["data"])
                    elif chunk["type"] == "content":
                        yield {"type": "content", "data": chunk["data"]}
                        final_message += chunk["data"]
                    elif chunk["type"] == "status":
                        yield {"type": "status", "data": chunk["data"]}

                # キャッシュに保存
                if use_cache and store_id and final_message:
                    cache_key = self._generate_cache_key(query, store_id)
                    self._set_to_cache(cache_key, final_message)

                yield {
                    "type": "done",
                    "data": {
                        "message": final_message,
                        "from_cache": False,
                        "intermediate_steps": intermediate_steps
                    }
                }
            else:
                # ツールなしで直接LLM呼び出し（ストリーミング）
                yield {"type": "status", "data": "回答を生成しています..."}

                from langchain_core.messages import HumanMessage, SystemMessage

                messages = [
                    SystemMessage(content=system_info),
                    HumanMessage(content=query)
                ]

                final_message = ""
                for chunk in self.llm_streaming.stream(messages):
                    if hasattr(chunk, 'content') and chunk.content:
                        yield {"type": "content", "data": chunk.content}
                        final_message += chunk.content

                yield {
                    "type": "done",
                    "data": {
                        "message": final_message,
                        "from_cache": False,
                        "intermediate_steps": []
                    }
                }

        except Exception as e:
            logger.error(f"Error in chat_stream: {e}", exc_info=True)
            yield {
                "type": "error",
                "data": f"エラーが発生しました: {str(e)}"
            }

    def _react_loop_stream(
        self,
        query: str,
        tools: List,
        system_info: str
    ) -> Iterator[Dict]:
        """
        ストリーミング対応のReActループ

        Yields:
            {"type": "status/tool_call/tool_result/content", "data": ...}
        """
        try:
            from langchain_core.messages import SystemMessage, HumanMessage, ToolMessage

            yield {"type": "status", "data": "ツールを選択しています..."}

            # System message
            system_message = SystemMessage(content=f"""{system_info}

CRITICAL: You do NOT have any prior knowledge about this restaurant's data.
You MUST use the provided tools to answer ALL questions about claims, sales, reports, etc.

For the question "先週のクレーム", you MUST call search_daily_reports tool with query="クレーム" and days=7.

Always respond in Japanese after retrieving data from tools.""")

            # Bind tools to LLM
            llm_with_tools = self.llm.bind_tools(tools)

            # Create messages
            messages = [system_message, HumanMessage(content=query)]

            # Invoke LLM with tools
            response = llm_with_tools.invoke(messages)

            # Check if tools were called
            if hasattr(response, 'tool_calls') and response.tool_calls:
                yield {"type": "status", "data": f"{len(response.tool_calls)}個のツールを実行しています..."}

                # Execute tool calls
                tool_results = []
                for tool_call in response.tool_calls:
                    tool_name = tool_call['name']
                    tool_args = tool_call['args']

                    yield {
                        "type": "tool_call",
                        "data": {
                            "tool": tool_name,
                            "args": tool_args
                        }
                    }

                    # Find and execute the tool
                    for tool in tools:
                        if tool.name == tool_name:
                            result_text = tool.invoke(tool_args)
                            tool_results.append(ToolMessage(
                                content=str(result_text),
                                tool_call_id=tool_call['id']
                            ))

                            yield {
                                "type": "tool_result",
                                "data": {
                                    "tool": tool_name,
                                    "action": tool_name,
                                    "action_input": str(tool_args),
                                    "observation": str(result_text),
                                    "result": str(result_text)[:200] + "..." if len(str(result_text)) > 200 else str(result_text)
                                }
                            }
                            break

                # Get final response with tool results (streaming)
                messages.append(response)
                messages.extend(tool_results)

                yield {"type": "status", "data": "回答を生成しています..."}

                llm_streaming_with_tools = self.llm_streaming.bind_tools(tools)
                for chunk in llm_streaming_with_tools.stream(messages):
                    if hasattr(chunk, 'content') and chunk.content:
                        yield {"type": "content", "data": chunk.content}
            else:
                # No tools called, just stream the response
                yield {"type": "status", "data": "回答を生成しています..."}
                if hasattr(response, 'content'):
                    yield {"type": "content", "data": response.content}

        except Exception as e:
            logger.error(f"Error in _react_loop_stream: {e}", exc_info=True)
            yield {"type": "error", "data": f"ツール実行エラー: {str(e)}"}
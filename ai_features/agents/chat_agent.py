import hashlib
import json
import asyncio
from typing import List, Dict, Optional, Iterator, Tuple
from datetime import datetime, timedelta
from functools import lru_cache

from langchain_core.tools import tool
from langchain_openai import ChatOpenAI

import logging
logger = logging.getLogger(__name__)


# ツール生成をキャッシュする（グローバル関数として定義）
@lru_cache(maxsize=100)
def _get_cached_tools_for_store(store_id: int) -> Tuple:
    """
    store_idをバインドしたツールリストを作成（キャッシュ対応）

    Args:
        store_id: 店舗ID

    Returns:
        ツールのタプル（lru_cacheのためにタプルで返す）
    """
    from ai_features.tools.search_tools import (
        search_daily_reports as _search_daily_reports,
        search_bbs_posts as _search_bbs_posts,
        search_manual,
        search_by_genre as _search_by_genre,
        search_by_location as _search_by_location,
        search_daily_reports_all_stores,
        search_bbs_posts_all_stores,
        search_by_genre_all_stores,
        search_by_location_all_stores
    )
    from ai_features.tools.analytics_tools import (
        get_claim_statistics as _get_claim_statistics,
        get_sales_trend as _get_sales_trend,
        get_cash_difference_analysis as _get_cash_difference_analysis,
        get_report_statistics as _get_report_statistics,
        get_monthly_goal_status as _get_monthly_goal_status,
        gather_topic_related_data as _gather_topic_related_data,
        compare_periods as _compare_periods,
        get_claim_statistics_all_stores,
        get_report_statistics_all_stores,
        gather_topic_related_data_all_stores
    )

    # Create tool functions with store_id bound via closure
    @tool
    def search_daily_reports(query: str = "", days: int = 30) -> str:
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
    def search_bbs_posts(query: str = "", days: int = 30) -> str:
        """
        Search bulletin board posts with full discussion threads (all comments included).
        Returns the complete conversation flow and conclusions (best answers) for each post.

        When to use this tool:
        - When checking discussions or opinions among staff members
        - When you need to understand how a discussion concluded
        - When searching for posts about specific topics with their comments

        Args:
            query: Search keyword (e.g., "シフト", "メニュー改善")
            days: Search period in days (default: 30)

        Returns:
            Posts with all comments, best_answer (if exists), and has_conclusion flag
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

    @tool
    def get_report_statistics(days: int = 30) -> str:
        """
        Get daily report statistics including genre breakdown and location analysis.

        When to use this tool:
        - When user wants an overview of daily reports (日報の全体像)
        - When analyzing report submission patterns
        - When checking genre or location distribution

        Args:
            days: Aggregation period in days (default: 30)
        """
        return _get_report_statistics.invoke({"store_id": store_id, "days": days})

    @tool
    def get_monthly_goal_status() -> str:
        """
        Get monthly goal information including current month's goal and achievement rate.

        When to use this tool:
        - When user asks about monthly goals or targets (月次目標, 目標達成)
        - When checking goal achievement status

        Returns:
            JSON string with current goal status and past goals
        """
        return _get_monthly_goal_status.invoke({"store_id": store_id})

    @tool
    def search_by_genre(query: str, genre: str, days: int = 60) -> str:
        """
        Search daily reports filtered by specific genre.

        When to use this tool:
        - When user specifically wants to search within a particular genre
        - When narrowing search to only claims (クレームのみ), only praise (賞賛のみ), etc.
        - Valid genres: claim, praise, accident, report, other

        Args:
            query: Search keyword
            genre: Genre filter (claim/praise/accident/report/other)
            days: Search period in days (default: 60)
        """
        return _search_by_genre.invoke({"query": query, "store_id": store_id, "genre": genre, "days": days})

    @tool
    def search_by_location(query: str, location: str, days: int = 60) -> str:
        """
        Search daily reports filtered by specific location.

        When to use this tool:
        - When user wants to search within a specific location
        - When analyzing problems in a particular area (キッチンだけ, ホールのみ, etc.)
        - Valid locations: kitchen, hall, cashier, toilet, other

        Args:
            query: Search keyword
            location: Location filter (kitchen/hall/cashier/toilet/other)
            days: Search period in days (default: 60)
        """
        return _search_by_location.invoke({"query": query, "store_id": store_id, "location": location, "days": days})

    @tool
    def gather_topic_related_data(topic: str, days: int = 30) -> str:
        """
        Gather comprehensive data about a topic from multiple sources (reports, BBS, statistics).

        When to use this tool:
        - When user asks for advice or recommendations (アドバイス頂戴, 改善策)
        - When you need full context about an issue from multiple sources
        - When analyzing a specific topic comprehensively

        Args:
            topic: Topic keyword (e.g., "クレーム", "売上", "接客")
            days: Search period in days (default: 30)

        Returns:
            Comprehensive data from daily reports, BBS, and relevant statistics
        """
        return _gather_topic_related_data.invoke({"topic": topic, "store_id": store_id, "days": days})

    @tool
    def compare_periods(metric: str, period1_days: int = 7, period2_days: int = 14) -> str:
        """
        Compare metrics between two time periods with statistical calculations.

        When to use this tool:
        - When user asks about changes or trends (先週と比べて, 変化, 推移)
        - When comparing current vs previous performance
        - Valid metrics: sales, claims, accidents, reports, cash_difference

        Args:
            metric: Metric to compare (sales/claims/accidents/reports/cash_difference)
            period1_days: Recent period days (default: 7)
            period2_days: Comparison period days (default: 14, means 8-14 days ago)

        Returns:
            Side-by-side comparison with calculated change rates
        """
        return _compare_periods.invoke({"store_id": store_id, "metric": metric, "period1_days": period1_days, "period2_days": period2_days})

    # ============================================================
    # 全店舗ツール（All Stores）
    # ============================================================

    @tool
    def search_daily_reports_all_stores_tool(query: str = "", days: int = 60) -> str:
        """
        Search daily reports across ALL stores for best practices and cross-store learning.

        When to use this tool:
        - When user explicitly mentions other stores (他店舗, 他の店, 他店)
        - When looking for best practices across all stores (全店舗, ベストプラクティス)
        - When user asks "how do other stores handle this?" (他店ではどう対応)
        - When comparing issues or solutions across multiple stores
        - Keywords: 全店舗, 他店舗, 他の店, 他店, ベストプラクティス, 事例を参考

        Args:
            query: Search keyword (e.g., "クレーム対応", "接客改善")
            days: Search period in days (default: 60)

        Returns:
            Search results from all stores with store names included
        """
        return search_daily_reports_all_stores.invoke({"query": query, "days": days})

    @tool
    def search_bbs_posts_all_stores_tool(query: str = "", days: int = 30) -> str:
        """
        Search BBS posts across ALL stores with full discussion threads (all comments included).
        Returns the complete conversation flow and conclusions (best answers) for each post.

        When to use this tool:
        - When user wants to see discussions from other stores (他店の意見, 他店舗の議論)
        - When looking for solutions implemented in other stores
        - When you need to understand how discussions concluded at other stores
        - Keywords: 全店舗, 他店舗の意見, 他店の議論

        Args:
            query: Search keyword (e.g., "シフト改善", "メニュー工夫")
            days: Search period in days (default: 30)

        Returns:
            Posts from all stores with all comments, best_answer, and has_conclusion flag
        """
        return search_bbs_posts_all_stores.invoke({"query": query, "days": days})

    @tool
    def search_by_genre_all_stores_tool(query: str, genre: str, days: int = 60) -> str:
        """
        Search daily reports by genre across ALL stores.

        When to use this tool:
        - When user wants to see how other stores handle specific genre issues
        - When comparing genre-specific patterns across stores
        - Keywords: 全店舗の + (クレーム/賞賛/事故/報告)

        Args:
            query: Search keyword
            genre: Genre filter (claim/praise/accident/report/other)
            days: Search period in days (default: 60)

        Returns:
            Genre-filtered results from all stores
        """
        return search_by_genre_all_stores.invoke({"query": query, "genre": genre, "days": days})

    @tool
    def search_by_location_all_stores_tool(query: str, location: str, days: int = 60) -> str:
        """
        Search daily reports by location across ALL stores.

        When to use this tool:
        - When analyzing location-specific issues across multiple stores
        - When comparing how different stores handle the same location issues
        - Keywords: 全店舗の + (キッチン/ホール/レジ/トイレ)

        Args:
            query: Search keyword
            location: Location filter (kitchen/hall/cashier/toilet/other)
            days: Search period in days (default: 60)

        Returns:
            Location-filtered results from all stores
        """
        return search_by_location_all_stores.invoke({"query": query, "location": location, "days": days})

    @tool
    def get_claim_statistics_all_stores_tool(days: int = 30) -> str:
        """
        Get claim statistics across ALL stores for comparison and trend analysis.

        When to use this tool:
        - When user asks to compare claims across all stores (全店舗のクレーム比較)
        - When analyzing overall company-wide claim trends
        - When identifying stores with high/low claim rates
        - Keywords: 全店舗のクレーム, 店舗間比較, クレーム率の比較

        Args:
            days: Aggregation period in days (default: 30)

        Returns:
            Claim statistics with store breakdown and overall trends
        """
        return get_claim_statistics_all_stores.invoke({"days": days})

    @tool
    def get_report_statistics_all_stores_tool(days: int = 30) -> str:
        """
        Get report statistics across ALL stores for activity comparison.

        When to use this tool:
        - When comparing report submission activity across stores
        - When analyzing overall reporting patterns company-wide
        - Keywords: 全店舗の日報統計, 店舗間の活動量比較

        Args:
            days: Aggregation period in days (default: 30)

        Returns:
            Report statistics with store breakdown and genre analysis
        """
        return get_report_statistics_all_stores.invoke({"days": days})

    @tool
    def gather_topic_related_data_all_stores_tool(topic: str, days: int = 30) -> str:
        """
        Gather comprehensive data about a topic from ALL stores.

        When to use this tool:
        - When user asks for advice based on all available data (全店舗の事例から)
        - When analyzing a topic comprehensively across the entire company
        - When looking for best practices from any store
        - Keywords: 全店舗で + トピック, 他店の事例も含めて

        Args:
            topic: Topic keyword (e.g., "クレーム", "売上", "接客")
            days: Search period in days (default: 30)

        Returns:
            Comprehensive data from reports, BBS, and statistics across all stores
        """
        return gather_topic_related_data_all_stores.invoke({"topic": topic, "days": days})

    tools = (
        # 自店舗ツール
        search_daily_reports,
        search_bbs_posts,
        search_manual,  # 全店舗共通（ナレッジベース）
        search_by_genre,
        search_by_location,
        get_claim_statistics,
        get_sales_trend,
        get_cash_difference_analysis,
        get_report_statistics,
        get_monthly_goal_status,
        gather_topic_related_data,
        compare_periods,
        # 全店舗ツール
        search_daily_reports_all_stores_tool,
        search_bbs_posts_all_stores_tool,
        search_by_genre_all_stores_tool,
        search_by_location_all_stores_tool,
        get_claim_statistics_all_stores_tool,
        get_report_statistics_all_stores_tool,
        gather_topic_related_data_all_stores_tool,
    )

    logger.info(f"Created and cached {len(tools)} tools for store_id={store_id}")
    return tools


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
        store_idをバインドしたツールリストを作成（キャッシュ使用）

        Args:
            store_id: 店舗ID

        Returns:
            ツールのリスト
        """
        # キャッシュされたグローバル関数を使用
        return list(_get_cached_tools_for_store(store_id))


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
- Store: {store_name} (ID: {store_id or "Unknown"})

## Your Mission: PDCA Cycle Support

You are NOT just a data retrieval assistant. You are a **strategic advisor** helping managers improve operations through the PDCA cycle:
- **Plan**: Help set realistic goals and create action plans
- **Do**: Monitor execution and provide real-time guidance
- **Check**: Analyze results and identify issues
- **Act**: Recommend specific improvements based on data

## Critical Rules
1. **ALWAYS use tools**: You have NO knowledge about this restaurant's data. You MUST use tools to retrieve ALL information.
2. **NEVER guess or assume**: Base your answers ONLY on actual data retrieved from tools.
3. **Check tool results carefully**:
   - If tool returns `"status": "success"` AND `"results"` has items → Data EXISTS, provide the information
   - If tool returns `"status": "no_data"` OR `"results": []` → Data does NOT exist, say "データがありません"
   - NEVER say "データがありません" when results actually contain data

## Available Tools (12 tools)

### Search Tools (5 tools)
- **search_daily_reports**: General search across all daily reports (best for exploratory queries)
- **search_by_genre**: Search within specific genre (claim/praise/accident/report/other)
- **search_by_location**: Search within specific location (kitchen/hall/cashier/toilet/other)
- **search_bbs_posts**: Search bulletin board posts with full discussion threads and conclusions
- **search_manual**: Search manuals and guidelines

### Analytics Tools (5 tools)
- **get_claim_statistics**: Claim counts, trends, category breakdown
- **get_sales_trend**: Sales data, customer count, daily/weekly trends
- **get_cash_difference_analysis**: Register discrepancies, plus/minus breakdown
- **get_report_statistics**: Overall daily report statistics by genre/location
- **get_monthly_goal_status**: Current month's goal and achievement rate

### PDCA Support Tools (2 tools)
- **gather_topic_related_data**: Comprehensive data collection from multiple sources (for advice/analysis)
- **compare_periods**: Period-to-period comparison with change rates (for trend analysis)

## Tool Selection Guidelines

### When user asks for ADVICE or RECOMMENDATIONS (アドバイス, 改善策, 提案):
→ Use **gather_topic_related_data** + multiple analytics tools (see detailed steps below)

### When user asks about CHANGES or TRENDS (変化, 推移, 比較):
→ Use **compare_periods** for quantitative comparison
Example: "先週と比べてクレームは増えた?" → compare_periods(metric="claims", period1_days=7, period2_days=14)

### When user asks about SPECIFIC CONTENT or DETAILS:
→ Use **search_daily_reports** or **search_bbs_posts** for general queries
→ Use **search_by_genre** when user asks specifically about a genre (クレーム/賞賛/事故/報告)
Example (general): "先週の問題" → search_daily_reports(query="問題", days=7)
Example (specific genre): "先週の事故" → search_by_genre(query="事故", genre="accident", days=7)
Example (specific genre): "クレームの内容" → search_by_genre(query="", genre="claim", days=30)

### When user asks about STATISTICS or COUNTS:
→ Use **analytics tools** (get_claim_statistics, get_sales_trend, etc.)
Example: "先週のクレーム件数" → get_claim_statistics(days=7)

### When user specifies GENRE or LOCATION filter:
→ Use **search_by_genre** or **search_by_location**
Example: "キッチンのクレーム" → search_by_location(query="クレーム", location="kitchen")

### When user asks about GOALS or TARGETS:
→ Use **get_monthly_goal_status**
Example: "今月の目標" → get_monthly_goal_status()

## Response Style
- Respond in Japanese (日本語で回答)
- Be concise and use bullet points
- Include specific numbers from tool results
- State conclusions first, then supporting details

## When Providing ADVICE (アドバイス・提案モード):

**Step 1: GATHER DATA** - Use multiple tools for comprehensive context
- gather_topic_related_data() for cross-source information
- Relevant analytics tools (get_sales_trend, get_claim_statistics, etc.)
- compare_periods() if trend analysis is needed

**Step 2: ANALYZE** - Identify patterns, gaps, root causes
- Calculate gaps: 目標 - 現状 = ギャップ
- Find correlations: クレーム↑ → 売上↓?
- Spot trends: 増加傾向 or 減少傾向?
- Check BBS for staff perspectives

**Step 3: RECOMMEND** - Provide specific, actionable advice

**Japanese Response Format:**

**📊 現状分析**
- [データから分かった現状を簡潔に]

**⚠️ 課題・ギャップ**
- [目標とのギャップ、問題点]

**💡 推奨アクション（優先度順）**
1. **[最優先]** [具体的な行動] → [期待される効果]
2. **[重要]** [具体的な行動] → [期待される効果]
3. [その他の施策]

**📈 根拠となるデータ**
- [使用したデータの要点]"""

            # ツールを使用する場合（ReActエージェント）
            if use_tools and store_id:
                # logger.info(f"Creating ReAct agent for store_id={store_id}")

                # ツール作成（キャッシュから取得）
                tools = self._create_tools_for_store(store_id)

                # create_react_agentを使用
                from langchain_core.messages import SystemMessage, HumanMessage, AIMessage

                # メッセージリストの作成（システムメッセージを先頭に追加）
                messages = [SystemMessage(content=system_info)]

                # チャット履歴を追加
                if chat_history:
                    for msg in chat_history:
                        if msg['role'] == 'user':
                            messages.append(HumanMessage(content=msg['content']))
                        elif msg['role'] == 'assistant':
                            messages.append(AIMessage(content=msg['content']))

                # 現在のクエリを追加
                messages.append(HumanMessage(content=query))

                # ReActエージェント作成（遅延インポート）
                from langgraph.prebuilt import create_react_agent
                agent = create_react_agent(
                    model=self.llm,
                    tools=tools
                )

                # エージェント実行
                result = agent.invoke({"messages": messages})

                # 結果を取得
                response_text = result["messages"][-1].content

                # intermediate_stepsの取得（LangGraphではメッセージ履歴から構築）
                intermediate_steps = []
                """
                total_tool_result_size = 0
                for msg in result["messages"]:
                    if hasattr(msg, 'tool_calls') and msg.tool_calls:
                        for tool_call in msg.tool_calls:
                            tool_name = tool_call.get('name', '')
                            logger.info(f"Tool called: {tool_name}")
                            intermediate_steps.append({
                                "thought": "",
                                "action": tool_name,
                                "action_input": str(tool_call.get('args', {})),
                                "observation": ""
                            })
                    elif msg.__class__.__name__ == 'ToolMessage':
                        # ToolMessageの場合は観測結果を記録
                        result_size = len(msg.content)
                        total_tool_result_size += result_size
                        if intermediate_steps:
                            intermediate_steps[-1]["observation"] = msg.content[:200]  # 最初の200文字
                            logger.info(f"  → Result size: {result_size:,} chars")
                """

            else:
                # ツールなしで直接LLM呼び出し
                logger.info(f"Invoking LLM without tools")
                from langchain_core.messages import SystemMessage, HumanMessage, AIMessage

                messages = [SystemMessage(content=system_info)]

                # Add chat history if provided
                if chat_history:
                    for msg in chat_history:
                        if msg['role'] == 'user':
                            messages.append(HumanMessage(content=msg['content']))
                        elif msg['role'] == 'assistant':
                            messages.append(AIMessage(content=msg['content']))

                # Add current query
                messages.append(HumanMessage(content=query))

                llm_response = self.llm.invoke(messages)
                # AIMessageの場合、contentを取得
                if hasattr(llm_response, 'content'):
                    response_text = llm_response.content
                else:
                    response_text = str(llm_response)
                intermediate_steps = []

            # 空の応答をチェック
            if not response_text or response_text.strip() in ['-', '', 'None']:
                response_text = "申し訳ございません。回答を生成できませんでした。別の質問をお試しください。"
                logger.warning(f"Empty or invalid response generated")

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

    def _react_loop_stream(
        self,
        query: str,
        tools: List,
        system_info: str,
        chat_history: Optional[List[Dict]] = None
    ):
        """
        ReActループのストリーミング版（最終回答のみトークン単位でストリーム）

        Args:
            query: ユーザーの質問
            tools: 利用可能なツールリスト
            system_info: システムプロンプト
            chat_history: チャット履歴

        Yields:
            str: レスポンスのトークンチャンク
        """
        try:
            from langchain_core.messages import SystemMessage, HumanMessage, AIMessage, ToolMessage

            # System message
            system_message = SystemMessage(content=system_info)

            # Bind tools to the LLM
            llm_with_tools = self.llm.bind_tools(tools)

            # Create messages with chat history
            messages = [system_message]

            # Add chat history if provided
            if chat_history:
                for msg in chat_history:
                    if msg['role'] == 'user':
                        messages.append(HumanMessage(content=msg['content']))
                    elif msg['role'] == 'assistant':
                        messages.append(AIMessage(content=msg['content']))

            # Add current query
            messages.append(HumanMessage(content=query))

            # Invoke LLM with tools
            logger.info(f"[Stream] Invoking LLM with tools for query: {query}")
            response = llm_with_tools.invoke(messages)

            # Check if tools were called
            if hasattr(response, 'tool_calls') and response.tool_calls:
                logger.info(f"[Stream] Tools called: {len(response.tool_calls)}")

                # Execute tool calls (non-streaming)
                tool_results = []
                for tool_call in response.tool_calls:
                    tool_name = tool_call['name']
                    tool_args = tool_call['args']
                    logger.info(f"[Stream] Executing tool: {tool_name}")

                    # Find and execute the tool
                    for tool in tools:
                        if tool.name == tool_name:
                            result_text = tool.invoke(tool_args)
                            tool_results.append(ToolMessage(
                                content=str(result_text),
                                tool_call_id=tool_call['id']
                            ))
                            break

                # Get final response with tool results - STREAMING
                messages.append(response)
                messages.extend(tool_results)

                logger.info(f"[Stream] Generating final response with streaming...")
                # 重要: 最終回答生成時はツールなしのLLMを使用
                # llm_with_tools を使うとLLMがまたツールを呼ぼうとしてしまう
                for chunk in self.llm.stream(messages):
                    if hasattr(chunk, 'content') and chunk.content:
                        yield chunk.content
                logger.info(f"[Stream] Final response streaming completed")
            else:
                logger.info("[Stream] No tools called, streaming direct response")
                # ツールが呼ばれなかった場合もストリーミング
                if hasattr(response, 'content') and response.content:
                    logger.info(f"[Stream] Direct response length: {len(response.content)}")
                    # トークン単位でストリーミング
                    for chunk in self.llm.stream(messages):
                        if hasattr(chunk, 'content') and chunk.content:
                            yield chunk.content
                else:
                    logger.error(f"[Stream] No content in response! Response type: {type(response)}, has content: {hasattr(response, 'content')}")
                    yield "エラー: 応答が空です"

        except Exception as e:
            logger.error(f"[Stream] Error in _react_loop_stream: {e}", exc_info=True)
            yield f"エラーが発生しました: {str(e)}"

    def chat_stream(
        self,
        query: str,
        user,
        chat_history: Optional[List[Dict]] = None,
        use_tools: bool = True
    ):
        """
        ストリーミングチャット実行（Generator）

        Args:
            query: ユーザーの質問
            user: Djangoユーザーオブジェクト
            chat_history: チャット履歴（オプション）
            use_tools: ツールを使用するか（デフォルト: True）

        Yields:
            str: レスポンスのチャンク（トークンごと）
        """
        try:
            # ユーザー情報を収集
            store_id = user.store.store_id if hasattr(user, 'store') and user.store else None
            store_name = user.store.store_name if hasattr(user, 'store') and user.store else "不明"

            # System prompt (same as chat method)
            system_info = f"""You are a restaurant operations support AI assistant. You help store managers and staff by retrieving accurate information from the database.

## Current Context
- Date/Time: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}
- Store: {store_name} (ID: {store_id or "Unknown"})

## Your Mission: PDCA Cycle Support

You are NOT just a data retrieval assistant. You are a **strategic advisor** helping managers improve operations through the PDCA cycle:
- **Plan**: Help set realistic goals and create action plans
- **Do**: Monitor execution and provide real-time guidance
- **Check**: Analyze results and identify issues
- **Act**: Recommend specific improvements based on data

## Critical Rules
1. **ALWAYS use tools**: You have NO knowledge about this restaurant's data. You MUST use tools to retrieve ALL information.
2. **NEVER guess or assume**: Base your answers ONLY on actual data retrieved from tools.
3. **Check tool results carefully**:
   - If tool returns `"status": "success"` AND `"results"` has items → Data EXISTS, provide the information
   - If tool returns `"status": "no_data"` OR `"results": []` → Data does NOT exist, say "データがありません"
   - NEVER say "データがありません" when results actually contain data

## Available Tools (12 tools)

### Search Tools (5 tools)
- **search_daily_reports**: General search across all daily reports (best for exploratory queries)
- **search_by_genre**: Search within specific genre (claim/praise/accident/report/other)
- **search_by_location**: Search within specific location (kitchen/hall/cashier/toilet/other)
- **search_bbs_posts**: Search bulletin board posts with full discussion threads and conclusions
- **search_manual**: Search manuals and guidelines

### Analytics Tools (5 tools)
- **get_claim_statistics**: Claim counts, trends, category breakdown
- **get_sales_trend**: Sales data, customer count, daily/weekly trends
- **get_cash_difference_analysis**: Register discrepancies, plus/minus breakdown
- **get_report_statistics**: Overall daily report statistics by genre/location
- **get_monthly_goal_status**: Current month's goal and achievement rate

### PDCA Support Tools (2 tools)
- **gather_topic_related_data**: Comprehensive data collection from multiple sources (for advice/analysis)
- **compare_periods**: Period-to-period comparison with change rates (for trend analysis)

## Tool Selection Guidelines

### When user asks for ADVICE or RECOMMENDATIONS (アドバイス, 改善策, 提案):
→ Use **gather_topic_related_data** + multiple analytics tools (see detailed steps below)

### When user asks about CHANGES or TRENDS (変化, 推移, 比較):
→ Use **compare_periods** for quantitative comparison
Example: "先週と比べてクレームは増えた?" → compare_periods(metric="claims", period1_days=7, period2_days=14)

### When user asks about SPECIFIC CONTENT or DETAILS:
→ Use **search_daily_reports** or **search_bbs_posts** for general queries
→ Use **search_by_genre** when user asks specifically about a genre (クレーム/賞賛/事故/報告)
Example (general): "先週の問題" → search_daily_reports(query="問題", days=7)
Example (specific genre): "先週の事故" → search_by_genre(query="事故", genre="accident", days=7)
Example (specific genre): "クレームの内容" → search_by_genre(query="", genre="claim", days=30)

### When user asks about STATISTICS or COUNTS:
→ Use **analytics tools** (get_claim_statistics, get_sales_trend, etc.)
Example: "先週のクレーム件数" → get_claim_statistics(days=7)

### When user specifies GENRE or LOCATION filter:
→ Use **search_by_genre** or **search_by_location**
Example: "キッチンのクレーム" → search_by_location(query="クレーム", location="kitchen")

### When user asks about GOALS or TARGETS:
→ Use **get_monthly_goal_status**
Example: "今月の目標" → get_monthly_goal_status()

## Response Style
- Respond in Japanese (日本語で回答)
- Be concise and use bullet points
- Include specific numbers from tool results
- State conclusions first, then supporting details

## When Providing ADVICE (アドバイス・提案モード):

**Step 1: GATHER DATA** - Use multiple tools for comprehensive context
- gather_topic_related_data() for cross-source information
- Relevant analytics tools (get_sales_trend, get_claim_statistics, etc.)
- compare_periods() if trend analysis is needed

**Step 2: ANALYZE** - Identify patterns, gaps, root causes
- Calculate gaps: 目標 - 現状 = ギャップ
- Find correlations: クレーム↑ → 売上↓?
- Spot trends: 増加傾向 or 減少傾向?
- Check BBS for staff perspectives

**Step 3: RECOMMEND** - Provide specific, actionable advice

**Japanese Response Format:**

**📊 現状分析**
- [データから分かった現状を簡潔に]

**⚠️ 課題・ギャップ**
- [目標とのギャップ、問題点]

**💡 推奨アクション（優先度順）**
1. **[最優先]** [具体的な行動] → [期待される効果]
2. **[重要]** [具体的な行動] → [期待される効果]
3. [その他の施策]

**📈 根拠となるデータ**
- [使用したデータの要点]"""

            # ツールを使用する場合（ReActエージェント）
            if use_tools and store_id:
                logger.debug(f"[Stream] Using manual ReAct loop with token streaming for store_id={store_id}")

                # ツール作成（キャッシュから取得）
                tools = self._create_tools_for_store(store_id)

                # 自作のReActループ（ストリーミング版）を使用
                # ツール実行後の最終回答生成時にトークン単位でストリーミング
                for token in self._react_loop_stream(
                    query=query,
                    tools=tools,
                    system_info=system_info,
                    chat_history=chat_history
                ):
                    yield token

                logger.debug(f"[Stream] Token streaming completed")

            else:
                # ツールなしで直接LLM呼び出し（ストリーミング）
                logger.debug(f"Streaming LLM without tools")
                from langchain_core.messages import SystemMessage, HumanMessage, AIMessage

                messages = [SystemMessage(content=system_info)]

                if chat_history:
                    for msg in chat_history:
                        if msg['role'] == 'user':
                            messages.append(HumanMessage(content=msg['content']))
                        elif msg['role'] == 'assistant':
                            messages.append(AIMessage(content=msg['content']))

                messages.append(HumanMessage(content=query))

                # ストリーミング実行
                for chunk in self.llm.stream(messages):
                    if hasattr(chunk, 'content') and chunk.content:
                        yield chunk.content

        except Exception as e:
            logger.error(f"Error in chat_stream: {e}", exc_info=True)
            yield f"エラーが発生しました: {str(e)}"

    # DEPRECATED: Replaced by create_react_agent
    '''
    def _react_loop(
        self,
        query: str,
        tools: List,
        system_info: str,
        chat_history: Optional[List[Dict]] = None,
        max_iterations: int = 5
    ) -> tuple[str, List[Dict]]:
        """
        LangGraph ReActエージェントを使用した実装（最新）

        Args:
            query: ユーザーの質問
            tools: 利用可能なツールリスト
            system_info: システムプロンプト
            chat_history: チャット履歴
            max_iterations: 最大反復回数

        Returns:
            (最終回答, 中間ステップリスト)
        """
        try:
            # Manual ReAct implementation with tool binding
            from langchain_core.messages import SystemMessage, HumanMessage, AIMessage, ToolMessage

            # System message with tool usage guidance
            system_message = SystemMessage(content=f"""{system_info}

## Tool Usage Examples

**Simple Queries:**
Q: "先週のクレーム件数は?" → get_claim_statistics(days=7)
Q: "先週のクレームの内容" → search_by_genre(query="", genre="claim", days=7)
Q: "先週の事故を教えて" → search_by_genre(query="", genre="accident", days=7)
Q: "今月の売上推移" → get_sales_trend(days=30)

**CRITICAL: When user asks specifically about クレーム/事故/賞賛/報告, use search_by_genre!**

**PDCA/Advisory Queries:** 🎯
Q: "今月の目標を達成するためのアドバイス頂戴"
→ Step 1: gather_topic_related_data(topic="目標")
→ Step 2: get_monthly_goal_status()
→ Step 3: get_sales_trend(days=30)
→ Step 4: Analyze and provide recommendations

Q: "クレームが増えている。原因と対策は?"
→ Step 1: gather_topic_related_data(topic="クレーム")
→ Step 2: compare_periods(metric="claims")
→ Step 3: Analyze patterns and recommend countermeasures

Q: "先月の事故について掲示板も踏まえてアドバイス"
→ Step 1: gather_topic_related_data(topic="事故")
→ Step 2: search_manual(query="事故対応")
→ Step 3: Provide prevention measures

REMEMBER:
- For ADVICE queries, use MULTIPLE tools and provide STRUCTURED recommendations.
- ALWAYS check if tool results contain actual data before saying "データがありません".
- If "results" array has items, DATA EXISTS - summarize and present it to the user.""")

            # Bind tools to the LLM
            llm_with_tools = self.llm.bind_tools(tools)

            # Create messages with chat history
            messages = [system_message]

            # Add chat history if provided
            if chat_history:
                for msg in chat_history:
                    if msg['role'] == 'user':
                        messages.append(HumanMessage(content=msg['content']))
                    elif msg['role'] == 'assistant':
                        messages.append(AIMessage(content=msg['content']))

            # Add current query
            messages.append(HumanMessage(content=query))

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
    '''

    def _estimate_tokens(self, text: str) -> int:
        """トークン数を推定"""
        return len(str(text)) // 4

    # DEPRECATED: Replaced by create_react_agent
    '''
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
    '''

    # DEPRECATED: Replaced by create_react_agent
    '''
    def _react_loop_parallel(
        self,
        query: str,
        tools: List,
        system_info: str,
        chat_history: Optional[List[Dict]] = None,
        max_iterations: int = 5
    ) -> tuple[str, List[Dict]]:
        """
        並列ツール実行対応のReActループ

        Args:
            query: ユーザーの質問
            tools: 利用可能なツールリスト
            system_info: システムプロンプト
            chat_history: チャット履歴
            max_iterations: 最大反復回数

        Returns:
            (最終回答, 中間ステップリスト)
        """
        try:
            from langchain_core.messages import SystemMessage, HumanMessage, AIMessage, ToolMessage

            # System message
            system_message = SystemMessage(content=f"""{system_info}

## Tool Usage Examples

**Simple Queries:**
Q: "先週のクレーム件数は?" → get_claim_statistics(days=7)
Q: "先週のクレームの内容" → search_by_genre(query="", genre="claim", days=7)
Q: "先週の事故を教えて" → search_by_genre(query="", genre="accident", days=7)
Q: "今月の売上推移" → get_sales_trend(days=30)

**CRITICAL: When user asks specifically about クレーム/事故/賞賛/報告, use search_by_genre!**

**PDCA/Advisory Queries:** 🎯
Q: "今月の目標を達成するためのアドバイス頂戴"
→ Step 1: gather_topic_related_data(topic="目標")
→ Step 2: get_monthly_goal_status()
→ Step 3: get_sales_trend(days=30)
→ Step 4: Analyze and provide recommendations

Q: "クレームが増えている。原因と対策は?"
→ Step 1: gather_topic_related_data(topic="クレーム")
→ Step 2: compare_periods(metric="claims")
→ Step 3: Analyze patterns and recommend countermeasures

Q: "先月の事故について掲示板も踏まえてアドバイス"
→ Step 1: gather_topic_related_data(topic="事故")
→ Step 2: search_manual(query="事故対応")
→ Step 3: Provide prevention measures

REMEMBER:
- For ADVICE queries, use MULTIPLE tools and provide STRUCTURED recommendations.
- ALWAYS check if tool results contain actual data before saying "データがありません".
- If "results" array has items, DATA EXISTS - summarize and present it to the user.""")

            # Bind tools to LLM
            llm_with_tools = self.llm.bind_tools(tools)

            # Create messages with chat history
            messages = [system_message]

            # Add chat history if provided
            if chat_history:
                for msg in chat_history:
                    if msg['role'] == 'user':
                        messages.append(HumanMessage(content=msg['content']))
                    elif msg['role'] == 'assistant':
                        messages.append(AIMessage(content=msg['content']))

            # Add current query
            messages.append(HumanMessage(content=query))

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
    '''
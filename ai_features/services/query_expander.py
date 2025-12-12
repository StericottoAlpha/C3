"""
クエリ拡張サービス
曖昧なクエリをLLMで複数の具体的なクエリに展開
"""
import logging
from typing import List, Optional, Dict
from datetime import datetime, timedelta
import json
import google.generativeai as genai
from django.conf import settings

logger = logging.getLogger(__name__)


class QueryExpander:
    """
    クエリ拡張サービス

    機能:
    - 曖昧な時間表現の正規化（昨日 → 2025-12-09）
    - 同義語展開（問題 → トラブル、クレーム、事故）
    - コンテキストに応じた具体化
    - 3-5個の具体的なクエリを生成
    """

    # Gemini設定
    MODEL_NAME = "gemini-1.5-flash"

    @classmethod
    def expand(
        cls,
        query: str,
        user,
        context: Optional[Dict] = None
    ) -> List[str]:
        """
        クエリを展開して複数の具体的なクエリを生成

        Args:
            query: 元のクエリ
            user: ユーザーオブジェクト
            context: 追加コンテキスト（オプション）

        Returns:
            展開されたクエリのリスト（3-5個）
        """
        try:
            # Geminiモデル設定
            genai.configure(api_key=settings.GEMINI_API_KEY)
            model = genai.GenerativeModel(cls.MODEL_NAME)

            # コンテキスト情報構築
            context_info = cls._build_context(user, context)

            # プロンプト構築
            prompt = cls._build_expansion_prompt(query, context_info)

            # LLM呼び出し
            response = model.generate_content(prompt)

            # レスポンス解析
            expanded_queries = cls._parse_response(response.text)

            # バリデーション
            if not expanded_queries or len(expanded_queries) < 1:
                logger.warning(f"Query expansion failed, using original: {query}")
                return [query]

            logger.info(f"Expanded query: {query} -> {expanded_queries}")
            return expanded_queries

        except Exception as e:
            logger.error(f"Error in query expansion: {e}")
            # フォールバック: 元のクエリを返す
            return [query]

    @classmethod
    def _build_context(cls, user, additional_context: Optional[Dict] = None) -> Dict:
        """
        ユーザーコンテキストを構築

        Args:
            user: ユーザーオブジェクト
            additional_context: 追加コンテキスト

        Returns:
            コンテキスト辞書
        """
        context = {
            'current_date': datetime.now().strftime('%Y-%m-%d'),
            'current_year': datetime.now().year,
            'current_month': datetime.now().month,
            'current_day': datetime.now().day,
        }

        # ユーザー情報
        if hasattr(user, 'store'):
            context['store_name'] = user.store.store_name
            context['store_id'] = user.store.store_id

        # ユーザー名
        context['user_name'] = user.get_full_name() or user.username

        # 曜日情報
        weekdays = ['月曜日', '火曜日', '水曜日', '木曜日', '金曜日', '土曜日', '日曜日']
        context['current_weekday'] = weekdays[datetime.now().weekday()]

        # 相対日付計算
        today = datetime.now().date()
        context['yesterday'] = (today - timedelta(days=1)).strftime('%Y-%m-%d')
        context['last_week'] = (today - timedelta(days=7)).strftime('%Y-%m-%d')
        context['last_month'] = (today - timedelta(days=30)).strftime('%Y-%m-%d')

        # 追加コンテキスト
        if additional_context:
            context.update(additional_context)

        return context

    @classmethod
    def _build_expansion_prompt(cls, query: str, context: Dict) -> str:
        """
        クエリ拡張用プロンプトを構築

        Args:
            query: 元のクエリ
            context: コンテキスト情報

        Returns:
            プロンプト文字列
        """
        prompt = f"""あなたは飲食店の業務アシスタントです。ユーザーからの曖昧なクエリを、より具体的な3-5個のクエリに展開してください。

# コンテキスト情報
- 現在日時: {context['current_date']} ({context['current_weekday']})
- 店舗: {context.get('store_name', '不明')}
- ユーザー: {context['user_name']}

# 相対日付参照
- 昨日: {context['yesterday']}
- 先週: {context['last_week']}
- 先月: {context['last_month']}

# ユーザークエリ
{query}

# 展開ルール
1. 曖昧な時間表現を具体的な日付に変換
   - 「昨日」→「{context['yesterday']}」
   - 「先週」→「{context['last_week']}から{context['current_date']}」
   - 「最近」→「過去7日間」

2. 抽象的な用語を具体的な同義語に展開
   - 「問題」→「トラブル」「クレーム」「事故」「不具合」
   - 「売上」→「売上高」「レジ金額」「売上実績」
   - 「スタッフ」→「従業員」「アルバイト」「社員」

3. 検索観点を多様化
   - 日付範囲の変更
   - カテゴリの追加
   - ジャンルの明示化

4. 3-5個の具体的なクエリを生成

# 出力フォーマット
JSON配列形式で返してください。他の説明は不要です。

例: ["具体的なクエリ1", "具体的なクエリ2", "具体的なクエリ3"]

# 出力
"""
        return prompt

    @classmethod
    def _parse_response(cls, response_text: str) -> List[str]:
        """
        LLMレスポンスを解析

        Args:
            response_text: LLMの生成テキスト

        Returns:
            展開されたクエリのリスト
        """
        try:
            # JSONマークダウンブロックを除去
            text = response_text.strip()
            if text.startswith('```json'):
                text = text[7:]
            if text.startswith('```'):
                text = text[3:]
            if text.endswith('```'):
                text = text[:-3]
            text = text.strip()

            # JSON解析
            queries = json.loads(text)

            # 文字列リストであることを確認
            if isinstance(queries, list):
                queries = [str(q) for q in queries if q and str(q).strip()]
                # 3-5個に制限
                return queries[:5]

            logger.warning(f"Unexpected response format: {response_text}")
            return []

        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse JSON response: {e}")
            logger.debug(f"Response text: {response_text}")

            # フォールバック: 改行区切りで分割
            lines = [line.strip() for line in response_text.split('\n') if line.strip()]
            # リストマーカーを除去
            cleaned = []
            for line in lines:
                line = line.lstrip('- ').lstrip('* ').lstrip('1234567890. ')
                if line and len(line) > 5:
                    cleaned.append(line)

            return cleaned[:5]

    @classmethod
    def normalize_date_expression(cls, query: str) -> str:
        """
        日付表現を正規化（簡易版）

        Args:
            query: クエリ文字列

        Returns:
            正規化されたクエリ
        """
        today = datetime.now().date()

        replacements = {
            '今日': today.strftime('%Y-%m-%d'),
            '昨日': (today - timedelta(days=1)).strftime('%Y-%m-%d'),
            '一昨日': (today - timedelta(days=2)).strftime('%Y-%m-%d'),
        }

        normalized = query
        for old, new in replacements.items():
            normalized = normalized.replace(old, new)

        return normalized

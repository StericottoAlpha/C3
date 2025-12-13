"""
解答精度テスト
多様なシードデータに対するReActエージェントの解答精度を評価
"""
import os
import sys
import django

# Djangoセットアップ
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'c3_app.settings')
django.setup()

from django.contrib.auth import get_user_model
from ai_features.agents import ChatAgent
import json

User = get_user_model()


class AnswerAccuracyTest:
    """解答精度テストクラス"""

    def __init__(self):
        self.agent = ChatAgent(
            model_name="llama3.1:latest",
            base_url="http://localhost:11434",
            temperature=0.1
        )
        self.user = User.objects.filter(store__store_name='A店').first()

        if not self.user:
            raise Exception("テストユーザーが見つかりません")

    def run_test(self, test_name: str, query: str, expected_keywords: list, expected_tool: str = None):
        """
        1つのテストケースを実行

        Args:
            test_name: テスト名
            query: 質問
            expected_keywords: 期待されるキーワード（回答に含まれるべき）
            expected_tool: 期待されるツール名（オプション）
        """
        print(f"\n{'='*70}")
        print(f"テスト: {test_name}")
        print(f"{'='*70}")
        print(f"質問: {query}")

        try:
            response = self.agent.chat(
                query=query,
                user=self.user,
                use_tools=True
            )

            message = response['message']
            intermediate_steps = response.get('intermediate_steps', [])

            print(f"\n回答:\n{message}\n")
            print(f"トークン数: {response['token_count']}")
            print(f"使用ツール数: {len(intermediate_steps)}")

            # 中間ステップの表示
            if intermediate_steps:
                print(f"\n--- 使用したツール ---")
                for i, step in enumerate(intermediate_steps, 1):
                    print(f"{i}. {step.get('action', 'N/A')}")

            # キーワードチェック
            print(f"\n--- キーワード検証 ---")
            found_keywords = []
            missing_keywords = []

            for keyword in expected_keywords:
                if keyword.lower() in message.lower():
                    found_keywords.append(keyword)
                    print(f"✅ '{keyword}' が含まれています")
                else:
                    missing_keywords.append(keyword)
                    print(f"❌ '{keyword}' が含まれていません")

            # ツールチェック
            if expected_tool:
                print(f"\n--- ツール検証 ---")
                used_tools = [step.get('action') for step in intermediate_steps]
                if expected_tool in used_tools:
                    print(f"✅ 期待されるツール '{expected_tool}' が使用されました")
                else:
                    print(f"❌ 期待されるツール '{expected_tool}' が使用されませんでした")
                    print(f"   実際に使用されたツール: {used_tools}")

            # 結果判定
            keyword_score = len(found_keywords) / len(expected_keywords) if expected_keywords else 1.0
            tool_score = 1.0 if (not expected_tool or expected_tool in used_tools) else 0.0

            total_score = (keyword_score + tool_score) / 2
            status = "✅ PASS" if total_score >= 0.7 else "❌ FAIL"

            print(f"\n--- スコア ---")
            print(f"キーワードスコア: {keyword_score:.1%} ({len(found_keywords)}/{len(expected_keywords)})")
            if expected_tool:
                print(f"ツールスコア: {tool_score:.1%}")
            print(f"総合スコア: {total_score:.1%}")
            print(f"判定: {status}")

            return {
                'test_name': test_name,
                'query': query,
                'response': message,
                'keyword_score': keyword_score,
                'tool_score': tool_score,
                'total_score': total_score,
                'passed': total_score >= 0.7
            }

        except Exception as e:
            print(f"❌ エラー: {e}")
            import traceback
            traceback.print_exc()
            return {
                'test_name': test_name,
                'query': query,
                'error': str(e),
                'passed': False
            }


def main():
    print("=" * 70)
    print("   ReAct Agent 解答精度テスト")
    print("=" * 70)

    tester = AnswerAccuracyTest()

    # テストケース定義
    test_cases = [
        {
            'name': 'クレーム検索（基本）',
            'query': '先週のクレームを教えて',
            'keywords': ['クレーム', '接客', '提供'],
            'tool': 'search_daily_reports'
        },
        {
            'name': 'クレーム検索（詳細）',
            'query': 'A店で最近発生したクレームの内容と対策を教えて',
            'keywords': ['クレーム', '対応', '改善'],
            'tool': 'search_daily_reports'
        },
        {
            'name': '売上分析',
            'query': '最近の売上推移はどう？',
            'keywords': ['売上', '推移', 'トレンド'],
            'tool': 'get_sales_trend'
        },
        {
            'name': '現金過不足分析',
            'query': '現金過不足の状況を教えて',
            'keywords': ['過不足', '違算', '現金'],
            'tool': 'get_cash_difference_analysis'
        },
        {
            'name': 'クレーム統計',
            'query': 'クレームの件数と傾向を分析して',
            'keywords': ['件数', 'クレーム', '傾向'],
            'tool': 'get_claim_statistics'
        },
        {
            'name': '賞賛検索',
            'query': 'お客様から褒められた内容を教えて',
            'keywords': ['賞賛', '褒め', '評価'],
            'tool': 'search_daily_reports'
        },
        {
            'name': '事故検索',
            'query': '設備トラブルや事故の記録は？',
            'keywords': ['事故', '設備', 'トラブル'],
            'tool': 'search_daily_reports'
        },
        {
            'name': '掲示板検索',
            'query': '動線改善についての議論を教えて',
            'keywords': ['動線', '改善', 'レイアウト'],
            'tool': 'search_bbs_posts'
        },
    ]

    results = []
    for test_case in test_cases:
        result = tester.run_test(
            test_name=test_case['name'],
            query=test_case['query'],
            expected_keywords=test_case['keywords'],
            expected_tool=test_case.get('tool')
        )
        results.append(result)

    # サマリー表示
    print("\n" + "=" * 70)
    print("   テスト結果サマリー")
    print("=" * 70)

    passed = sum(1 for r in results if r.get('passed', False))
    total = len(results)

    for result in results:
        status = "✅ PASS" if result.get('passed', False) else "❌ FAIL"
        score = result.get('total_score', 0)
        print(f"{status} [{score:.0%}] {result['test_name']}")

    print(f"\n合計: {passed}/{total} テスト合格 ({passed/total:.0%})")

    # 詳細結果をJSONファイルに保存
    with open('test_answer_accuracy_results.json', 'w', encoding='utf-8') as f:
        json.dump(results, f, ensure_ascii=False, indent=2)
    print(f"\n詳細結果を test_answer_accuracy_results.json に保存しました")

    return passed == total


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)

"""
ReAct Agent ツール実行テスト
ツールを使用したReActエージェントの動作を確認

判定基準:
1. 応答速度: 15秒以内
2. ツール使用: 1つ以上のツールを使用
3. 回答精度: 質問に対する適切な回答
"""
import os
import sys
import django
import time

# Djangoセットアップ
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'c3_app.settings')
django.setup()

from django.contrib.auth import get_user_model
from ai_features.agents import ChatAgent

User = get_user_model()


def test_react_with_tools():
    """ReActエージェントでツールを使用するテスト"""
    print("\n=== ReAct Agent ツール実行テスト ===")

    try:
        # テストユーザー取得
        user = User.objects.first()

        if not user:
            print("❌ テストユーザーが見つかりません")
            return False

        print(f"テストユーザー: {user.user_id}")
        if hasattr(user, 'store') and user.store:
            print(f"店舗ID: {user.store.store_id}")
            print(f"店舗名: {user.store.store_name}")
        else:
            print("⚠️  店舗情報なし（ツールなしモードで実行）")

        # Agent初期化（環境変数から設定を取得）
        use_openai = os.environ.get('USE_OPENAI', 'False').lower() == 'true'
        openai_api_key = os.environ.get('OPENAI_API_KEY', '')
        openai_model = os.environ.get('OPENAI_MODEL', 'gpt-4o-mini')

        if use_openai and openai_api_key:
            agent = ChatAgent(
                model_name=openai_model,
                temperature=0.0,
                use_openai=True,
                openai_api_key=openai_api_key
            )
        else:
            agent = ChatAgent(
                model_name="llama3.1:latest",
                base_url="http://localhost:11434",
                temperature=0.1,
                use_openai=False
            )

        # ツールを使いそうな質問と期待キーワード
        test_cases = [
            ("先週のクレームを教えて", ["クレーム"]),
            ("最近の売上推移はどう？", ["売上"]),
            ("現金過不足の状況は？", ["現金", "過不足"]),
        ]

        all_passed = True
        for query, expected_keywords in test_cases:
            print(f"\n{'='*60}")
            print(f"質問: {query}")
            print(f"{'='*60}")

            start_time = time.time()
            response = agent.chat(
                query=query,
                user=user,
                use_tools=True
            )
            response_time = time.time() - start_time

            print(f"\n回答:\n{response['message']}")
            print(f"\nトークン数: {response['token_count']}")
            print(f"応答時間: {response_time:.2f}秒")

            # 中間ステップの表示
            intermediate_steps = response.get('intermediate_steps', [])
            if intermediate_steps:
                print(f"\n--- 中間ステップ ({len(intermediate_steps)}件) ---")
                for i, step in enumerate(intermediate_steps, 1):
                    print(f"\nステップ {i}:")
                    print(f"  思考: {step.get('thought', 'N/A')}")
                    print(f"  行動: {step.get('action', 'N/A')}")
                    print(f"  行動入力: {step.get('action_input', 'N/A')}")
                    observation = step.get('observation', 'N/A')
                    if len(str(observation)) > 200:
                        observation = str(observation)[:200] + '...'
                    print(f"  観察結果: {observation}")

            # 判定基準
            print(f"\n--- 判定結果 ---")
            criteria_passed = 0
            criteria_total = 3

            # 1. 応答速度（15秒以内）
            speed_threshold = 15.0
            if response_time <= speed_threshold:
                print(f"✅ 応答速度: {response_time:.2f}秒")
                criteria_passed += 1
            else:
                print(f"❌ 応答速度: {response_time:.2f}秒 (> {speed_threshold}秒)")

            # 2. ツール使用
            if len(intermediate_steps) >= 1:
                print(f"✅ ツール使用: {len(intermediate_steps)}個")
                criteria_passed += 1
            else:
                print(f"❌ ツール使用: ツール未使用")

            # 3. 回答精度（期待キーワードが含まれているか）
            answer = response['message']
            keywords_found = [kw for kw in expected_keywords if kw in answer]
            if keywords_found:
                print(f"✅ 回答精度: 期待キーワード含む ({', '.join(keywords_found)})")
                criteria_passed += 1
            else:
                print(f"❌ 回答精度: 期待キーワード不足 (期待: {', '.join(expected_keywords)})")

            # テストケース判定
            if criteria_passed == criteria_total:
                print(f"✅ このテストケース合格 (3/3)")
            elif criteria_passed >= 2:
                print(f"⚠️  このテストケース部分合格 ({criteria_passed}/3)")
                all_passed = False
            else:
                print(f"❌ このテストケース不合格 ({criteria_passed}/3)")
                all_passed = False

            print(f"\n{'='*60}\n")

        if all_passed:
            print("✅ ReActエージェントツールテスト完了（全テストケース合格）")
        else:
            print("⚠️  ReActエージェントツールテスト完了（一部テストケース不合格）")
        return all_passed

    except Exception as e:
        print(f"❌ テスト失敗: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_simple_chat_without_tools():
    """ツールなしの簡単なチャット（比較用）"""
    print("\n=== ツールなしチャット（比較用） ===")

    try:
        user = User.objects.first()

        if not user:
            print("❌ テストユーザーが見つかりません")
            return False

        agent = ChatAgent(
            model_name="llama3.1:latest",
            base_url="http://localhost:11434",
            temperature=0.1
        )

        query = "こんにちは"
        print(f"質問: {query}")

        response = agent.chat(
            query=query,
            user=user,
            use_tools=False
        )

        print(f"回答: {response['message']}")
        print(f"中間ステップ数: {len(response.get('intermediate_steps', []))}")

        print("✅ ツールなしチャット成功")
        return True

    except Exception as e:
        print(f"❌ テスト失敗: {e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    print("=" * 60)
    print("   ReAct Agent 統合テスト")
    print("=" * 60)

    results = []

    # Test 1: ツールなしチャット
    results.append(("ツールなしチャット", test_simple_chat_without_tools()))

    # Test 2: ReActエージェントツール実行
    results.append(("ReActツール実行", test_react_with_tools()))

    # 結果サマリー
    print("\n" + "=" * 60)
    print("   テスト結果サマリー")
    print("=" * 60)
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{test_name}: {status}")

    total_tests = len(results)
    passed_tests = sum(1 for _, result in results if result)
    print(f"\n合計: {passed_tests}/{total_tests} テスト合格")

    return all(result for _, result in results)


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)

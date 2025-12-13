"""
ReAct Agent ツール実行テスト
ツールを使用したReActエージェントの動作を確認
"""
import os
import sys
import django

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

        # Agent初期化
        agent = ChatAgent(
            model_name="llama3.1:latest",
            base_url="http://localhost:11434",
            temperature=0.1
        )

        # ツールを使いそうな質問
        queries = [
            "先週のクレームを教えて",
            "最近の売上推移はどう？",
            "現金過不足の状況は？",
        ]

        for query in queries:
            print(f"\n{'='*60}")
            print(f"質問: {query}")
            print(f"{'='*60}")

            response = agent.chat(
                query=query,
                user=user,
                use_tools=True
            )

            print(f"\n回答:\n{response['message']}")
            print(f"\nトークン数: {response['token_count']}")

            # 中間ステップの表示
            if response.get('intermediate_steps'):
                print(f"\n--- 中間ステップ ({len(response['intermediate_steps'])}件) ---")
                for i, step in enumerate(response['intermediate_steps'], 1):
                    print(f"\nステップ {i}:")
                    print(f"  思考: {step.get('thought', 'N/A')}")
                    print(f"  行動: {step.get('action', 'N/A')}")
                    print(f"  行動入力: {step.get('action_input', 'N/A')}")
                    print(f"  観察結果: {step.get('observation', 'N/A')[:200]}...")
            else:
                print("\n⚠️  中間ステップなし（ツールは使用されませんでした）")

            print(f"\n{'='*60}\n")

        print("✅ ReActエージェントツールテスト完了")
        return True

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

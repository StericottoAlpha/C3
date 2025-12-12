"""
AI Chat Agent 統合テスト
Ollamaとの接続、ツール呼び出し、回答生成をテスト
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


def test_ollama_connection():
    """Ollama接続テスト"""
    print("\n=== Test 1: Ollama接続確認 ===")
    try:
        import requests
        response = requests.get("http://localhost:11434/api/tags", timeout=5)
        if response.status_code == 200:
            models = response.json().get('models', [])
            print(f"✅ Ollama接続成功")
            print(f"利用可能なモデル: {[m.get('name') for m in models]}")
            return True
        else:
            print(f"❌ Ollama接続エラー: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Ollama接続失敗: {e}")
        return False


def test_agent_initialization():
    """Agent初期化テスト"""
    print("\n=== Test 2: Agent初期化 ===")
    try:
        agent = ChatAgent(
            model_name="llama3.2:3b",
            base_url="http://localhost:11434",
            temperature=0.1
        )
        print(f"✅ Agent初期化成功")
        print(f"モデル: {agent.model_name}")
        print(f"LLM: {type(agent.llm).__name__}")
        return True
    except Exception as e:
        print(f"❌ Agent初期化失敗: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_simple_chat():
    """簡単なチャットテスト"""
    print("\n=== Test 3: 簡単なチャット ===")
    try:
        # テストユーザー取得（user_idで検索）
        user = User.objects.first()

        if not user:
            print("❌ テストユーザーが見つかりません")
            return False

        print(f"テストユーザー: {user.user_id} ({user.email})")

        # Agent初期化
        agent = ChatAgent(
            model_name="llama3.1:latest",  # 既存のモデルを使用
            base_url="http://localhost:11434",
            temperature=0.1
        )

        # シンプルな質問
        query = "こんにちは"
        print(f"\n質問: {query}")

        response = agent.chat(
            query=query,
            user=user
        )

        print(f"\n回答: {response['message']}")
        print(f"トークン数: {response['token_count']}")
        print(f"ツール使用数: {len(response.get('intermediate_steps', []))}")

        print("✅ チャットテスト成功")
        return True

    except Exception as e:
        print(f"❌ チャットテスト失敗: {e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    print("===========================================")
    print("   AI Chat Agent 統合テスト")
    print("===========================================")

    results = []

    # Test 1: Ollama接続
    results.append(("Ollama接続", test_ollama_connection()))

    # Test 2: Agent初期化
    results.append(("Agent初期化", test_agent_initialization()))

    # Test 3: 簡単なチャット（Ollamaが応答する場合のみ）
    if results[0][1]:  # Ollama接続成功の場合
        results.append(("簡単なチャット", test_simple_chat()))

    # 結果サマリー
    print("\n===========================================")
    print("   テスト結果サマリー")
    print("===========================================")
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

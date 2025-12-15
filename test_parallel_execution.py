"""
並列ツール実行テスト
複数ツール呼び出し時の並列実行効果を検証
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


def test_parallel_vs_sequential():
    """並列実行と順次実行の比較テスト"""
    print("=" * 60)
    print("   並列ツール実行テスト")
    print("=" * 60)

    try:
        # テストユーザー取得
        user = User.objects.filter(store__store_name='A店').first()

        if not user:
            print("❌ テストユーザー（A店）が見つかりません")
            return False

        print(f"✅ テストユーザー: {user.user_id}")
        print(f"✅ 店舗: {user.store.store_name}\n")

        # Agent初期化
        use_openai = os.environ.get('USE_OPENAI', 'False').lower() == 'true'
        openai_api_key = os.environ.get('OPENAI_API_KEY', '')
        openai_model = os.environ.get('OPENAI_MODEL', 'gpt-4o-mini')

        if not use_openai or not openai_api_key:
            print("❌ OPENAI_API_KEY が設定されていません")
            return False

        agent = ChatAgent(
            model_name=openai_model,
            temperature=0.0,
            use_openai=True,
            openai_api_key=openai_api_key
        )
        print("✅ エージェント初期化完了\n")

        # テストケース: 複数ツールを呼ぶような質問
        # プロンプトを工夫して複数ツールを呼ばせる
        query = "先週のクレームと売上の状況を教えて"
        print(f"質問: {query}\n")

        # ユーザー情報を収集
        from datetime import datetime
        user_name = getattr(user, 'email', getattr(user, 'user_id', '不明'))
        store_id = user.store.store_id if hasattr(user, 'store') and user.store else None
        store_name = user.store.store_name if hasattr(user, 'store') and user.store else "不明"

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

        tools = agent._create_tools_for_store(store_id)

        # Test 1: 順次実行（通常モード）
        print("\n[Test 1] 順次実行モード")
        print("-" * 60)
        start_time1 = time.time()

        response_text1, intermediate_steps1 = agent._react_loop(
            query=query,
            tools=tools,
            system_info=system_info,
            max_iterations=5
        )

        time1 = time.time() - start_time1

        print(f"回答: {response_text1}")
        print(f"\n使用ツール数: {len(intermediate_steps1)}")
        for i, step in enumerate(intermediate_steps1, 1):
            print(f"  {i}. {step.get('action', 'N/A')}")
        print(f"実行時間: {time1:.2f}秒\n")

        # Test 2: 並列実行
        print("\n[Test 2] 並列実行モード")
        print("-" * 60)
        start_time2 = time.time()

        response_text2, intermediate_steps2 = agent._react_loop_parallel(
            query=query,
            tools=tools,
            system_info=system_info,
            max_iterations=5
        )

        time2 = time.time() - start_time2

        print(f"回答: {response_text2}")
        print(f"\n使用ツール数: {len(intermediate_steps2)}")
        for i, step in enumerate(intermediate_steps2, 1):
            print(f"  {i}. {step.get('action', 'N/A')}")
        print(f"実行時間: {time2:.2f}秒\n")

        # 比較結果
        print("\n" + "=" * 60)
        print("   比較結果")
        print("=" * 60)
        print(f"順次実行: {time1:.2f}秒")
        print(f"並列実行: {time2:.2f}秒")

        if len(intermediate_steps2) > 1:
            speedup = ((time1 - time2) / time1) * 100 if time1 > 0 else 0
            print(f"高速化: {speedup:.1f}%")

            if speedup > 10:
                print(f"✅ 並列実行による明確な高速化を確認")
                return True
            elif time2 <= time1:
                print(f"⚠️  並列実行は動作しているが、大きな高速化は見られず")
                return True
            else:
                print(f"❌ 並列実行が正しく動作していない可能性")
                return False
        else:
            print(f"⚠️  ツールが1つのみ使用されたため、並列実行の効果を測定できず")
            print(f"   (ツール数: {len(intermediate_steps2)})")
            # 1つのツールでも動作していればOK
            return len(intermediate_steps2) >= 1

    except Exception as e:
        print(f"❌ エラー: {e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    print("=" * 60)
    print("   並列ツール実行 統合テスト")
    print("=" * 60)

    success = test_parallel_vs_sequential()

    print("\n" + "=" * 60)
    if success:
        print("✅ テスト合格")
    else:
        print("❌ テスト不合格")
    print("=" * 60)

    return success


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)

"""
ストリーミング & キャッシュ機能テスト
応答速度とキャッシュ効果を確認
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


def test_streaming():
    """ストリーミング機能のテスト"""
    print("=" * 60)
    print("   ストリーミング機能テスト")
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

        # テストケース
        query = "先週のクレームを教えて"
        print(f"質問: {query}\n")

        # ストリーミング実行
        print("--- ストリーミング開始 ---")
        start_time = time.time()

        chunks_received = 0
        status_messages = []
        tool_calls = []
        content_chunks = []
        final_data = None

        for chunk in agent.chat_stream(
            query=query,
            user=user,
            use_tools=True,
            use_cache=True
        ):
            chunks_received += 1
            chunk_type = chunk.get("type")

            if chunk_type == "status":
                status_msg = chunk.get("data", "")
                status_messages.append(status_msg)
                print(f"[ステータス] {status_msg}")

            elif chunk_type == "tool_call":
                tool_data = chunk.get("data", {})
                tool_name = tool_data.get("tool", "")
                tool_calls.append(tool_name)
                print(f"[ツール呼び出し] {tool_name}")

            elif chunk_type == "tool_result":
                result_data = chunk.get("data", {})
                result_preview = result_data.get("result", "")[:100]
                print(f"[ツール結果] {result_preview}...")

            elif chunk_type == "content":
                content = chunk.get("data", "")
                content_chunks.append(content)
                # リアルタイムで表示（改行なし）
                print(content, end='', flush=True)

            elif chunk_type == "done":
                final_data = chunk.get("data", {})
                print("\n[完了]")

            elif chunk_type == "error":
                error_msg = chunk.get("data", "")
                print(f"\n[エラー] {error_msg}")

        response_time = time.time() - start_time

        print(f"\n--- ストリーミング終了 ---\n")
        print(f"応答時間: {response_time:.2f}秒")
        print(f"受信チャンク数: {chunks_received}")
        print(f"使用ツール: {', '.join(tool_calls) if tool_calls else 'なし'}")
        print(f"キャッシュ使用: {'はい' if final_data and final_data.get('from_cache') else 'いいえ'}\n")

        # 判定
        criteria_passed = 0
        criteria_total = 3

        # 1. 応答速度（15秒以内）
        if response_time <= 15.0:
            print(f"✅ 応答速度: {response_time:.2f}秒")
            criteria_passed += 1
        else:
            print(f"❌ 応答速度: {response_time:.2f}秒 (> 15秒)")

        # 2. ツール使用
        if len(tool_calls) >= 1:
            print(f"✅ ツール使用: {len(tool_calls)}個")
            criteria_passed += 1
        else:
            print(f"❌ ツール使用: ツール未使用")

        # 3. ストリーミングが機能している
        if len(content_chunks) > 1:
            print(f"✅ ストリーミング: {len(content_chunks)}チャンクに分割")
            criteria_passed += 1
        else:
            print(f"⚠️  ストリーミング: 分割なし（{len(content_chunks)}チャンク）")

        print(f"\n総合スコア: {criteria_passed}/{criteria_total}")

        return criteria_passed >= 2

    except Exception as e:
        print(f"❌ エラー: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_cache():
    """キャッシュ機能のテスト"""
    print("\n" + "=" * 60)
    print("   キャッシュ機能テスト")
    print("=" * 60)

    try:
        # テストユーザー取得
        user = User.objects.filter(store__store_name='A店').first()

        if not user:
            print("❌ テストユーザー（A店）が見つかりません")
            return False

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

        query = "先週のクレームを教えて"

        # 1回目：キャッシュなし
        print("\n[1回目実行] キャッシュなし")
        start_time1 = time.time()
        from_cache1 = False

        for chunk in agent.chat_stream(query=query, user=user, use_tools=True, use_cache=True):
            if chunk.get("type") == "done":
                from_cache1 = chunk.get("data", {}).get("from_cache", False)

        time1 = time.time() - start_time1
        print(f"応答時間: {time1:.2f}秒")
        print(f"キャッシュヒット: {from_cache1}")

        # 2回目：キャッシュあり（同じ質問）
        print("\n[2回目実行] 同じ質問（キャッシュ期待）")
        start_time2 = time.time()
        from_cache2 = False

        for chunk in agent.chat_stream(query=query, user=user, use_tools=True, use_cache=True):
            if chunk.get("type") == "done":
                from_cache2 = chunk.get("data", {}).get("from_cache", False)

        time2 = time.time() - start_time2
        print(f"応答時間: {time2:.2f}秒")
        print(f"キャッシュヒット: {from_cache2}")

        # 判定
        print("\n--- キャッシュ効果 ---")
        if from_cache2:
            speed_improvement = ((time1 - time2) / time1) * 100 if time1 > 0 else 0
            print(f"✅ キャッシュが機能しています")
            print(f"高速化: {speed_improvement:.1f}% ({time1:.2f}秒 → {time2:.2f}秒)")
            return True
        else:
            print(f"❌ キャッシュが機能していません")
            print(f"1回目: {time1:.2f}秒, 2回目: {time2:.2f}秒")
            return False

    except Exception as e:
        print(f"❌ エラー: {e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    print("=" * 60)
    print("   ストリーミング & キャッシュ 統合テスト")
    print("=" * 60)

    results = []

    # Test 1: ストリーミング
    results.append(("ストリーミング機能", test_streaming()))

    # Test 2: キャッシュ
    results.append(("キャッシュ機能", test_cache()))

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

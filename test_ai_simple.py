"""
シンプルなAIエージェントテスト
1つのテストケースで動作確認

判定基準:
1. 応答速度: 10秒以内
2. ツール使用: 1つ以上のツールを使用
3. 回答精度: データに基づいた適切な回答
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


def main():
    print("=" * 60)
    print("   AI Agent シンプルテスト")
    print("=" * 60)

    try:
        # 環境変数からAI設定を取得
        use_openai = os.environ.get('USE_OPENAI', 'False').lower() == 'true'
        openai_api_key = os.environ.get('OPENAI_API_KEY', '')
        openai_model = os.environ.get('OPENAI_MODEL', 'gpt-4o-mini')
        ollama_base_url = os.environ.get('OLLAMA_BASE_URL', 'http://localhost:11434')
        ollama_model = os.environ.get('OLLAMA_MODEL', 'llama3.2:3b')

        print(f"\n【AI設定】")
        print(f"モード: {'OpenAI' if use_openai else 'Ollama'}")
        if use_openai:
            print(f"モデル: {openai_model}")
            print(f"APIキー: {'設定済み' if openai_api_key else '未設定'}")
        else:
            print(f"モデル: {ollama_model}")
            print(f"ベースURL: {ollama_base_url}")
        print()

        # テストユーザー取得
        user = User.objects.filter(store__store_name='A店').first()

        if not user:
            print("❌ テストユーザー（A店）が見つかりません")
            return False

        print(f"✅ テストユーザー: {user.user_id}")
        print(f"✅ 店舗: {user.store.store_name}")

        # Agent初期化（環境変数に基づく）
        if use_openai:
            if not openai_api_key:
                print("❌ OPENAI_API_KEY が設定されていません")
                return False
            agent = ChatAgent(
                model_name=openai_model,
                temperature=0.0,  # GPT最適化: 決定論的な出力
                use_openai=True,
                openai_api_key=openai_api_key
            )
        else:
            agent = ChatAgent(
                model_name=ollama_model,
                base_url=ollama_base_url,
                temperature=0.1,
                use_openai=False
            )
        print("✅ エージェント初期化完了")

        # テストケース
        query = "先週のクレームを教えて"
        print(f"\n{'='*60}")
        print(f"質問: {query}")
        print(f"{'='*60}\n")

        # チャット実行（時間測定）
        start_time = time.time()
        response = agent.chat(
            query=query,
            user=user,
            use_tools=True
        )
        response_time = time.time() - start_time

        # 結果表示
        print(f"回答:\n{response['message']}\n")
        print(f"トークン数: {response['token_count']}")
        print(f"応答時間: {response_time:.2f}秒")

        intermediate_steps = response.get('intermediate_steps', [])
        print(f"使用ツール数: {len(intermediate_steps)}")

        # ツール使用の詳細
        if intermediate_steps:
            print(f"\n--- 使用したツール ---")
            for i, step in enumerate(intermediate_steps, 1):
                print(f"{i}. {step.get('action', 'N/A')}")
                print(f"   入力: {step.get('action_input', 'N/A')}")
                observation = step.get('observation', 'N/A')
                if len(str(observation)) > 200:
                    observation = str(observation)[:200] + '...'
                print(f"   結果: {observation}\n")

        # 判定基準
        print(f"\n{'='*60}")
        print("判定結果")
        print(f"{'='*60}")

        criteria_passed = 0
        criteria_total = 3

        # 1. 応答速度チェック（10秒以内）
        speed_threshold = 10.0
        if response_time <= speed_threshold:
            print(f"✅ 応答速度: {response_time:.2f}秒 (<= {speed_threshold}秒)")
            criteria_passed += 1
        else:
            print(f"❌ 応答速度: {response_time:.2f}秒 (> {speed_threshold}秒)")

        # 2. ツール使用チェック（1つ以上）
        if len(intermediate_steps) >= 1:
            print(f"✅ ツール使用: {len(intermediate_steps)}個のツールを使用")
            criteria_passed += 1
        else:
            print(f"❌ ツール使用: ツールが使用されませんでした")

        # 3. 回答精度チェック
        # 質問に対して適切な回答をしているかチェック
        answer = response['message'].lower()
        is_accurate = False

        # クレームに関する回答が含まれているか
        if 'クレーム' in response['message'] or 'くれーむ' in answer or 'claim' in answer:
            # 件数や状況についての言及があるか
            if any(word in response['message'] for word in ['件', '0', 'ありません', 'なし', 'ございません']):
                is_accurate = True
                print(f"✅ 回答精度: クレームに関する適切な回答")
                criteria_passed += 1
            else:
                print(f"❌ 回答精度: クレームについての具体的な情報が不足")
        else:
            print(f"❌ 回答精度: 質問に対する回答が不適切")

        # 最終判定
        score = criteria_passed / criteria_total
        print(f"\n総合スコア: {score:.0%} ({criteria_passed}/{criteria_total})")

        if criteria_passed == criteria_total:
            print("✅ テスト合格（全基準クリア）")
            return True
        elif criteria_passed >= 2:
            print("⚠️  テスト部分合格（一部基準未達成）")
            return True
        else:
            print("❌ テスト不合格")
            return False

    except Exception as e:
        print(f"❌ エラー: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)

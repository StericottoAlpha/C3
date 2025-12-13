"""
シンプルなAIエージェントテスト
1つのテストケースで動作確認
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


def main():
    print("=" * 60)
    print("   AI Agent シンプルテスト")
    print("=" * 60)

    try:
        # テストユーザー取得
        user = User.objects.filter(store__store_name='A店').first()

        if not user:
            print("❌ テストユーザー（A店）が見つかりません")
            return False

        print(f"✅ テストユーザー: {user.user_id}")
        print(f"✅ 店舗: {user.store.store_name}")

        # Agent初期化
        agent = ChatAgent(
            model_name="llama3.1:latest",
            base_url="http://localhost:11434",
            temperature=0.1
        )
        print("✅ エージェント初期化完了")

        # テストケース
        query = "先週のクレームを教えて"
        print(f"\n{'='*60}")
        print(f"質問: {query}")
        print(f"{'='*60}\n")

        # チャット実行
        response = agent.chat(
            query=query,
            user=user,
            use_tools=True
        )

        # 結果表示
        print(f"回答:\n{response['message']}\n")
        print(f"トークン数: {response['token_count']}")

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
        else:
            print("\n⚠️  ツールは使用されませんでした")

        # キーワードチェック
        expected_keywords = ['クレーム', '接客', '提供']
        print(f"\n--- キーワード検証 ---")
        found = 0
        for keyword in expected_keywords:
            if keyword.lower() in response['message'].lower():
                print(f"✅ '{keyword}' が含まれています")
                found += 1
            else:
                print(f"❌ '{keyword}' が含まれていません")

        score = found / len(expected_keywords)
        print(f"\nスコア: {score:.0%} ({found}/{len(expected_keywords)})")

        if score >= 0.5:
            print("✅ テスト合格")
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

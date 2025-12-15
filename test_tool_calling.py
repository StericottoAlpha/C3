"""
ツールコーリングの直接テスト
ChatOpenAIでツールが正しく呼ばれるか確認
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'c3_app.settings')
django.setup()

from langchain_openai import ChatOpenAI
from langchain_core.tools import tool
from langchain_core.messages import HumanMessage

# テストツール定義
@tool
def get_weather(location: str) -> str:
    """Get the weather for a location."""
    return f"The weather in {location} is sunny"

# ChatOpenAI初期化
openai_api_key = os.environ.get('OPENAI_API_KEY', '')
llm = ChatOpenAI(
    model="gpt-4o-mini",
    temperature=0.0,
    api_key=openai_api_key
)

# ツールをバインド
llm_with_tools = llm.bind_tools([get_weather])

# テスト実行
print("=" * 60)
print("Testing direct tool calling with ChatOpenAI")
print("=" * 60)

query = "What's the weather in Tokyo?"
print(f"\nQuery: {query}\n")

result = llm_with_tools.invoke([HumanMessage(content=query)])

print(f"Result type: {type(result)}")
print(f"Result content: {result.content}")
print(f"Has tool_calls: {hasattr(result, 'tool_calls')}")

if hasattr(result, 'tool_calls'):
    print(f"Tool calls: {result.tool_calls}")

if hasattr(result, 'additional_kwargs'):
    tool_calls = result.additional_kwargs.get('tool_calls', [])
    print(f"\nTool calls in additional_kwargs: {len(tool_calls)}")
    for tc in tool_calls:
        print(f"  - {tc}")

print("\n" + "=" * 60)
if hasattr(result, 'tool_calls') and result.tool_calls:
    print("✅ Tool calling works!")
else:
    print("❌ Tool calling failed")

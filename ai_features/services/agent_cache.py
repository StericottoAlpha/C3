"""
ChatAgent Caching Service
ChatAgentのキャッシュ管理サービス
"""
import hashlib
import logging
import threading
from collections import OrderedDict
from typing import Optional

logger = logging.getLogger(__name__)


class ChatAgentCache:
    """
    ChatAgentをキャッシュして使い回すサービス

    Features:
    - APIキーのハッシュ化
    - LRUキャッシュによるメモリ制限
    - スレッドセーフ
    """

    _cache: OrderedDict = OrderedDict()
    _lock = threading.Lock()
    _max_cache_size = 10  # 最大キャッシュ数

    @classmethod
    def _hash_api_key(cls, api_key: str) -> str:
        """
        APIキーをSHA256でハッシュ化

        Args:
            api_key: OpenAI APIキー

        Returns:
            ハッシュ化されたAPIキー（16文字）
        """
        return hashlib.sha256(api_key.encode()).hexdigest()[:16]

    @classmethod
    def get_agent(
        cls,
        model_name: str,
        temperature: float,
        api_key: str
    ) -> 'ChatAgent':
        """
        ChatAgentをキャッシュから取得または新規作成

        Args:
            model_name: OpenAIモデル名（例: 'gpt-4o-mini'）
            temperature: 温度パラメータ
            api_key: OpenAI APIキー

        Returns:
            ChatAgentインスタンス
        """
        # APIキーをハッシュ化してキャッシュキーを生成
        api_key_hash = cls._hash_api_key(api_key)
        cache_key = (model_name, temperature, api_key_hash)

        with cls._lock:
            # キャッシュにヒットした場合
            if cache_key in cls._cache:
                # LRU: 最近使用したものを末尾に移動
                cls._cache.move_to_end(cache_key)
                logger.debug(f"Cache hit for agent: {model_name} (temp={temperature})")
                return cls._cache[cache_key]

            # キャッシュミス: 新規作成
            from ai_features.agents.chat_agent import ChatAgent

            agent = ChatAgent(
                model_name=model_name,
                temperature=temperature,
                openai_api_key=api_key
            )

            # キャッシュに追加
            cls._cache[cache_key] = agent
            logger.info(f"Created and cached new agent: {model_name} (temp={temperature})")

            # LRU: キャッシュサイズ超過時は古いものから削除
            if len(cls._cache) > cls._max_cache_size:
                oldest_key = next(iter(cls._cache))
                removed_agent = cls._cache.pop(oldest_key)
                logger.info(f"Evicted oldest agent from cache: {oldest_key[0]}")

                # メモリ解放のヒント（オプショナル）
                del removed_agent

            return agent

    @classmethod
    def clear_cache(cls):
        """キャッシュをクリア"""
        with cls._lock:
            cls._cache.clear()
            logger.info("Agent cache cleared")

    @classmethod
    def get_cache_info(cls) -> dict:
        """キャッシュ情報を取得（デバッグ用）"""
        with cls._lock:
            return {
                'cache_size': len(cls._cache),
                'max_cache_size': cls._max_cache_size,
                'cached_agents': [
                    {
                        'model_name': key[0],
                        'temperature': key[1],
                        'api_key_hash': key[2]
                    }
                    for key in cls._cache.keys()
                ]
            }

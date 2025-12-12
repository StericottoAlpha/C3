"""
ナレッジチャンキングサービス
マニュアル専用のテキストチャンキング機能
"""
import logging
import re
from typing import List, Dict

logger = logging.getLogger(__name__)


class KnowledgeChunker:
    """
    マニュアル専用チャンキングクラス

    特徴:
    - チャンクサイズ: 500-1000トークン（実績データより大きめ）
    - オーバーラップ: 100トークン
    - セマンティック境界を考慮（章・節区切り）
    """

    # チャンクサイズ設定
    MIN_CHUNK_SIZE = 500  # トークン
    MAX_CHUNK_SIZE = 1000  # トークン
    OVERLAP_SIZE = 100  # トークン

    # 1トークン ≈ 4文字（日本語）の概算
    CHARS_PER_TOKEN = 4

    @classmethod
    def chunk_text(
        cls,
        text: str,
        document_title: str = "",
        preserve_structure: bool = True
    ) -> List[Dict[str, any]]:
        """
        テキストをチャンクに分割

        Args:
            text: 分割するテキスト
            document_title: ドキュメントタイトル（メタデータ用）
            preserve_structure: 構造保持するかどうか（章・節を考慮）

        Returns:
            チャンクのリスト
            [
                {
                    'content': チャンクテキスト,
                    'chunk_index': チャンク番号,
                    'metadata': {
                        'chapter': 章,
                        'section': 節,
                        'start_char': 開始文字位置,
                        'end_char': 終了文字位置,
                    }
                },
                ...
            ]
        """
        if not text.strip():
            return []

        if preserve_structure:
            # 構造を考慮した分割
            return cls._chunk_with_structure(text, document_title)
        else:
            # シンプルな固定サイズ分割
            return cls._chunk_fixed_size(text, document_title)

    @classmethod
    def _chunk_with_structure(cls, text: str, document_title: str) -> List[Dict[str, any]]:
        """
        構造を考慮したチャンキング

        章・節の見出しを認識してセマンティックな境界で分割

        Args:
            text: 分割するテキスト
            document_title: ドキュメントタイトル

        Returns:
            チャンクのリスト
        """
        chunks = []
        sections = cls._extract_sections(text)

        current_chunk = ""
        current_metadata = {}
        chunk_index = 0

        for section in sections:
            section_text = section['content']
            section_size = len(section_text) // cls.CHARS_PER_TOKEN

            # 現在のチャンクサイズ
            current_size = len(current_chunk) // cls.CHARS_PER_TOKEN

            # セクションが大きすぎる場合は分割
            if section_size > cls.MAX_CHUNK_SIZE:
                # 現在のチャンクを保存
                if current_chunk:
                    chunks.append({
                        'content': current_chunk.strip(),
                        'chunk_index': chunk_index,
                        'metadata': current_metadata.copy()
                    })
                    chunk_index += 1
                    current_chunk = ""

                # 大きなセクションを分割
                sub_chunks = cls._split_large_section(section_text, section)
                for sub_chunk in sub_chunks:
                    chunks.append({
                        'content': sub_chunk.strip(),
                        'chunk_index': chunk_index,
                        'metadata': section.get('metadata', {})
                    })
                    chunk_index += 1

            # 追加するとMAXを超える場合
            elif current_size + section_size > cls.MAX_CHUNK_SIZE:
                # 現在のチャンクを保存
                if current_chunk:
                    chunks.append({
                        'content': current_chunk.strip(),
                        'chunk_index': chunk_index,
                        'metadata': current_metadata.copy()
                    })
                    chunk_index += 1

                # 新しいチャンクを開始
                current_chunk = section_text
                current_metadata = section.get('metadata', {})

            # 追加してもMINを下回る、または適切なサイズ
            else:
                if current_chunk:
                    # オーバーラップ処理
                    overlap_text = cls._get_overlap(current_chunk, cls.OVERLAP_SIZE)
                    current_chunk += "\n\n" + section_text
                else:
                    current_chunk = section_text
                    current_metadata = section.get('metadata', {})

        # 最後のチャンクを追加
        if current_chunk:
            chunks.append({
                'content': current_chunk.strip(),
                'chunk_index': chunk_index,
                'metadata': current_metadata
            })

        return chunks

    @classmethod
    def _chunk_fixed_size(cls, text: str, document_title: str) -> List[Dict[str, any]]:
        """
        固定サイズでのチャンキング

        Args:
            text: 分割するテキスト
            document_title: ドキュメントタイトル

        Returns:
            チャンクのリスト
        """
        chunks = []
        chunk_size_chars = cls.MAX_CHUNK_SIZE * cls.CHARS_PER_TOKEN
        overlap_chars = cls.OVERLAP_SIZE * cls.CHARS_PER_TOKEN

        start = 0
        chunk_index = 0

        while start < len(text):
            end = start + chunk_size_chars

            # 文の途中で切らないよう調整
            if end < len(text):
                # 次の改行または句点を探す
                for delimiter in ['\n\n', '\n', '。', '．']:
                    next_delim = text.find(delimiter, end)
                    if next_delim != -1 and next_delim < end + 100:
                        end = next_delim + len(delimiter)
                        break

            chunk_text = text[start:end].strip()

            if chunk_text:
                chunks.append({
                    'content': chunk_text,
                    'chunk_index': chunk_index,
                    'metadata': {
                        'start_char': start,
                        'end_char': end,
                    }
                })
                chunk_index += 1

            # 次のチャンク開始位置（オーバーラップあり）
            start = end - overlap_chars

        return chunks

    @classmethod
    def _extract_sections(cls, text: str) -> List[Dict[str, any]]:
        """
        テキストからセクション（章・節）を抽出

        Args:
            text: テキスト

        Returns:
            セクションのリスト
        """
        sections = []

        # 章・節パターン（例: "第1章", "1.1", "## タイトル"など）
        section_patterns = [
            r'^第?\s*(\d+)\s*章(.*)$',  # 第1章
            r'^(\d+)\.(\d+)\s+(.*)$',  # 1.1 節
            r'^#+\s+(.*)$',  # Markdown見出し
            r'^\[Page\s+\d+/\d+\]$',  # PDFページ区切り
        ]

        lines = text.split('\n')
        current_section = {'content': '', 'metadata': {}}

        for line in lines:
            is_header = False

            for pattern in section_patterns:
                match = re.match(pattern, line.strip())
                if match:
                    # 前のセクションを保存
                    if current_section['content'].strip():
                        sections.append(current_section)

                    # 新しいセクション開始
                    current_section = {
                        'content': line + '\n',
                        'metadata': {
                            'section_header': line.strip()
                        }
                    }
                    is_header = True
                    break

            if not is_header:
                current_section['content'] += line + '\n'

        # 最後のセクションを追加
        if current_section['content'].strip():
            sections.append(current_section)

        return sections if sections else [{'content': text, 'metadata': {}}]

    @classmethod
    def _split_large_section(cls, text: str, section_info: dict) -> List[str]:
        """
        大きなセクションを分割

        Args:
            text: セクションテキスト
            section_info: セクション情報

        Returns:
            分割されたテキストのリスト
        """
        chunks = []
        chunk_size_chars = cls.MAX_CHUNK_SIZE * cls.CHARS_PER_TOKEN

        paragraphs = text.split('\n\n')
        current_chunk = ""

        for para in paragraphs:
            para_size = len(para)

            if len(current_chunk) + para_size > chunk_size_chars:
                if current_chunk:
                    chunks.append(current_chunk.strip())
                current_chunk = para
            else:
                if current_chunk:
                    current_chunk += "\n\n" + para
                else:
                    current_chunk = para

        if current_chunk:
            chunks.append(current_chunk.strip())

        return chunks

    @classmethod
    def _get_overlap(cls, text: str, overlap_tokens: int) -> str:
        """
        テキストの末尾からオーバーラップ部分を取得

        Args:
            text: テキスト
            overlap_tokens: オーバーラップトークン数

        Returns:
            オーバーラップテキスト
        """
        overlap_chars = overlap_tokens * cls.CHARS_PER_TOKEN
        return text[-overlap_chars:] if len(text) > overlap_chars else text

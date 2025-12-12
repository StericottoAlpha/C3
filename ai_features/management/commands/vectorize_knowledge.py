"""
ナレッジドキュメント（マニュアル）をベクトル化するDjango管理コマンド

使用例:
    python manage.py vectorize_knowledge --all
    python manage.py vectorize_knowledge --document-id 1
    python manage.py vectorize_knowledge --unvectorized
"""
from django.core.management.base import BaseCommand, CommandError
from django.utils import timezone
from tqdm import tqdm

from ai_features.models import KnowledgeDocument, KnowledgeVector
from ai_features.services import DocumentParser, KnowledgeChunker
from ai_features.services import EmbeddingService


class Command(BaseCommand):
    help = 'ナレッジドキュメントをベクトル化してKnowledgeVectorテーブルに保存します'

    def add_arguments(self, parser):
        parser.add_argument(
            '--all',
            action='store_true',
            help='全てのナレッジドキュメントをベクトル化',
        )
        parser.add_argument(
            '--document-id',
            type=int,
            help='特定のドキュメントIDをベクトル化',
        )
        parser.add_argument(
            '--unvectorized',
            action='store_true',
            help='未ベクトル化のドキュメントのみ処理',
        )
        parser.add_argument(
            '--force',
            action='store_true',
            help='既存のベクトルを削除して再ベクトル化',
        )

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('ナレッジドキュメントのベクトル化処理を開始します...\n'))

        # 特定のドキュメント処理
        if options['document_id']:
            self.vectorize_single_document(options['document_id'], options['force'])
            return

        # 未ベクトル化のみ処理
        if options['unvectorized']:
            self.vectorize_unvectorized_documents(options['force'])
            return

        # 全ドキュメント処理
        if options['all']:
            self.vectorize_all_documents(options['force'])
            return

        # オプションが指定されていない場合
        raise CommandError(
            'オプションを指定してください。--help でヘルプを表示します。'
        )

    def vectorize_single_document(self, document_id: int, force: bool = False):
        """特定のドキュメントをベクトル化"""
        self.stdout.write(f'ドキュメントID {document_id} をベクトル化中...')

        try:
            document = KnowledgeDocument.objects.get(document_id=document_id)
        except KnowledgeDocument.DoesNotExist:
            self.stdout.write(self.style.ERROR(f'✗ ドキュメントID {document_id} が見つかりません'))
            return

        result = self._vectorize_document(document, force)

        if result['success']:
            self.stdout.write(
                self.style.SUCCESS(
                    f'✓ ドキュメントID {document_id} のベクトル化が完了しました '
                    f'({result["chunk_count"]}チャンク)'
                )
            )
        else:
            self.stdout.write(
                self.style.ERROR(
                    f'✗ ドキュメントID {document_id} のベクトル化に失敗しました: {result["error"]}'
                )
            )

    def vectorize_unvectorized_documents(self, force: bool = False):
        """未ベクトル化のドキュメントを処理"""
        self.stdout.write(self.style.WARNING('\n=== 未ベクトル化ドキュメントの処理 ==='))

        documents = KnowledgeDocument.objects.filter(vectorized=False, is_active=True)
        total = documents.count()

        if total == 0:
            self.stdout.write('ベクトル化が必要なドキュメントはありません')
            return

        self._process_documents(documents, force)

    def vectorize_all_documents(self, force: bool = False):
        """全てのドキュメントをベクトル化"""
        self.stdout.write(self.style.WARNING('\n=== 全ドキュメントのベクトル化 ==='))

        documents = KnowledgeDocument.objects.filter(is_active=True)
        total = documents.count()

        if total == 0:
            self.stdout.write('ベクトル化するドキュメントがありません')
            return

        self._process_documents(documents, force)

    def _process_documents(self, documents, force: bool = False):
        """ドキュメントのバッチ処理"""
        total = documents.count()
        success_count = 0
        error_count = 0
        chunk_count = 0

        for document in tqdm(documents, desc='ドキュメントをベクトル化中', unit='件'):
            result = self._vectorize_document(document, force)
            if result['success']:
                success_count += 1
                chunk_count += result['chunk_count']
            else:
                error_count += 1
                self.stdout.write(
                    self.style.WARNING(
                        f'\n警告: {document.title} の処理に失敗 - {result["error"]}'
                    )
                )

        self.stdout.write(
            self.style.SUCCESS(
                f'\n\nベクトル化完了: '
                f'成功 {success_count}件, '
                f'失敗 {error_count}件, '
                f'合計 {total}件\n'
                f'生成チャンク数: {chunk_count}'
            )
        )

    def _vectorize_document(self, document: KnowledgeDocument, force: bool = False) -> dict:
        """
        単一ドキュメントのベクトル化処理

        Args:
            document: KnowledgeDocumentインスタンス
            force: 既存ベクトルを削除して再作成

        Returns:
            {
                'success': bool,
                'chunk_count': int,
                'error': str or None
            }
        """
        try:
            # 既存のベクトルを確認
            existing_vectors = KnowledgeVector.objects.filter(document=document)
            if existing_vectors.exists():
                if force:
                    existing_vectors.delete()
                else:
                    return {
                        'success': False,
                        'chunk_count': 0,
                        'error': '既にベクトル化済みです（--forceで強制再作成）'
                    }

            # ファイルパスを取得
            file_path = document.file_path.path

            # テキスト抽出
            text = DocumentParser.extract_text(file_path, document.file_type)
            if not text:
                return {
                    'success': False,
                    'chunk_count': 0,
                    'error': 'テキスト抽出に失敗しました'
                }

            # チャンキング
            chunks = KnowledgeChunker.chunk_text(
                text=text,
                document_title=document.title,
                preserve_structure=True
            )

            if not chunks:
                return {
                    'success': False,
                    'chunk_count': 0,
                    'error': 'チャンク生成に失敗しました'
                }

            # 各チャンクをベクトル化
            created_vectors = []
            for chunk_data in chunks:
                # ベクトル生成
                embedding = EmbeddingService.generate_embedding(chunk_data['content'])
                if embedding is None:
                    continue

                # メタデータ構築
                metadata = {
                    'category': document.category,
                    'document_title': document.title,
                    'version': document.version,
                    'chunk_index': chunk_data['chunk_index'],
                    **chunk_data.get('metadata', {})
                }

                # KnowledgeVector作成
                vector = KnowledgeVector.objects.create(
                    document=document,
                    document_type=document.document_type,
                    content=chunk_data['content'],
                    metadata=metadata,
                    embedding=embedding
                )
                created_vectors.append(vector)

            # ドキュメントのベクトル化状態を更新
            document.vectorized = True
            document.vectorized_at = timezone.now()
            document.save()

            return {
                'success': True,
                'chunk_count': len(created_vectors),
                'error': None
            }

        except Exception as e:
            return {
                'success': False,
                'chunk_count': 0,
                'error': str(e)
            }

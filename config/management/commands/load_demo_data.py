"""
本番デモ用シードデータをSQLから読み込むコマンド

使用方法:
    python manage.py load_demo_data

オプション:
    --truncate: 既存データを削除してから実行
    --dry-run: 実際には実行せず、SQLの内容を表示
"""

from django.core.management.base import BaseCommand
from django.db import connection
from pathlib import Path


class Command(BaseCommand):
    help = '本番デモ用シードデータをSQLファイルから読み込みます'

    def add_arguments(self, parser):
        parser.add_argument(
            '--truncate',
            action='store_true',
            help='既存データを削除してから実行',
        )
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='実際には実行せず、SQLの内容を表示',
        )

    def handle(self, *args, **options):
        sql_file = Path(__file__).resolve().parent / 'demo_seed.sql'

        if not sql_file.exists():
            self.stderr.write(
                self.style.ERROR(f'SQLファイルが見つかりません: {sql_file}')
            )
            return

        # SQLファイルを読み込み
        with open(sql_file, 'r', encoding='utf-8') as f:
            sql_content = f.read()

        if options['dry_run']:
            self.stdout.write(self.style.WARNING('=== DRY RUN モード ==='))
            self.stdout.write('以下のSQLが実行されます:\n')
            # 最初の500文字だけ表示
            self.stdout.write(sql_content[:500] + '\n...(省略)...')
            return

        if options['truncate']:
            self.stdout.write(self.style.WARNING('既存データを削除しています...'))
            truncate_sql = """
                TRUNCATE
                    ai_chat_history,
                    bbs_comment_reactions,
                    bbs_reactions,
                    bbs_comments,
                    bbs_posts,
                    daily_reports,
                    store_daily_performances,
                    monthly_goals,
                    document_vectors,
                    knowledge_vectors
                RESTART IDENTITY CASCADE;

                DELETE FROM users WHERE user_id != 'admin';
                DELETE FROM stores WHERE store_id != 1;
            """
            try:
                with connection.cursor() as cursor:
                    cursor.execute(truncate_sql)
                self.stdout.write(self.style.SUCCESS('既存データを削除しました'))
            except Exception as e:
                self.stderr.write(
                    self.style.ERROR(f'データ削除中にエラーが発生しました: {e}')
                )
                return

        self.stdout.write('デモデータを読み込んでいます...')

        try:
            with connection.cursor() as cursor:
                cursor.execute(sql_content)

            self.stdout.write(self.style.SUCCESS('デモデータの読み込みが完了しました！'))

            # 読み込み結果の確認
            self.stdout.write('\n=== 読み込み結果 ===')
            tables_to_check = [
                ('stores', '店舗'),
                ('users', 'ユーザー'),
                ('store_daily_performances', '店舗日次実績'),
                ('daily_reports', '日報'),
                ('bbs_posts', '掲示板投稿'),
                ('bbs_comments', '掲示板コメント'),
                ('bbs_reactions', '掲示板リアクション'),
                ('monthly_goals', '月次目標'),
                ('ai_chat_history', 'AIチャット履歴'),
            ]

            with connection.cursor() as cursor:
                for table_name, display_name in tables_to_check:
                    cursor.execute(f'SELECT COUNT(*) FROM {table_name}')
                    count = cursor.fetchone()[0]
                    self.stdout.write(f'  {display_name}: {count}件')

            self.stdout.write(self.style.WARNING(
                '\n注意: ベクトルデータは別途 python manage.py vectorize_all で生成してください'
            ))
            self.stdout.write(self.style.WARNING(
                '注意: パスワードはデモ用（password123）です。本番運用前に変更してください'
            ))

        except Exception as e:
            self.stderr.write(
                self.style.ERROR(f'デモデータの読み込み中にエラーが発生しました: {e}')
            )
            raise

"""
本番デモ環境セットアップコマンド

デモデータの投入からベクトル化まで一括で実行します。

オプション:
    --truncate: 既存データを削除してから投入
    --skip-seed: シードデータ投入をスキップ（ベクトル化のみ実行）
    --skip-vectorize: ベクトル化をスキップ
    --password: デモユーザーのパスワード（デフォルト: password123）
"""

from django.core.management.base import BaseCommand
from django.db import connection
from django.contrib.auth import get_user_model
from pathlib import Path

User = get_user_model()


class Command(BaseCommand):
    help = '本番デモ環境をセットアップします（データ投入 + ベクトル化）'

    def add_arguments(self, parser):
        parser.add_argument(
            '--truncate',
            action='store_true',
            help='既存データを削除してから投入',
        )
        parser.add_argument(
            '--skip-seed',
            action='store_true',
            help='シードデータ投入をスキップ',
        )
        parser.add_argument(
            '--skip-vectorize',
            action='store_true',
            help='ベクトル化をスキップ',
        )

    def handle(self, *args, **options):
        self.stdout.write(self.style.WARNING('=== 本番デモ環境セットアップ開始 ===\n'))

        # 0. 既存データの削除（--truncate オプション指定時）
        if options['truncate']:
            self._truncate_data()

        # 1. シードデータ投入
        if not options['skip_seed']:
            self._load_seed_data()
        else:
            self.stdout.write('シードデータ投入をスキップしました\n')

        # 2. ベクトル化
        if not options['skip_vectorize']:
            self._vectorize_all()
        else:
            self.stdout.write('ベクトル化をスキップしました\n')

        self.stdout.write(self.style.SUCCESS('\n=== セットアップ完了 ==='))

    def _truncate_data(self):
        """既存データを削除"""
        self.stdout.write(self.style.WARNING('0. 既存データを削除中...\n'))

        truncate_sql = """
            -- 依存関係を考慮した順序で削除
            TRUNCATE
                document_vectors,
                knowledge_vectors,
                ai_chat_history,
                bbs_comment_reactions,
                bbs_reactions,
                bbs_comments,
                bbs_posts,
                report_images,
                daily_reports,
                store_daily_performances,
                monthly_goals
            RESTART IDENTITY CASCADE;

            -- ユーザーと店舗は外部キー制約があるため個別に削除
            DELETE FROM users;
            DELETE FROM stores;
        """

        try:
            with connection.cursor() as cursor:
                cursor.execute(truncate_sql)
            self.stdout.write(self.style.SUCCESS('既存データを削除しました\n'))
        except Exception as e:
            self.stderr.write(
                self.style.ERROR(f'データ削除中にエラー: {e}')
            )
            raise

    def _load_seed_data(self):
        """SQLファイルからシードデータを読み込む"""
        self.stdout.write(self.style.WARNING('1. シードデータを投入中...\n'))

        sql_file = Path(__file__).resolve().parent / 'demo_seed.sql'

        if not sql_file.exists():
            self.stderr.write(
                self.style.ERROR(f'SQLファイルが見つかりません: {sql_file}')
            )
            return

        with open(sql_file, 'r', encoding='utf-8') as f:
            sql_content = f.read()

        try:
            with connection.cursor() as cursor:
                cursor.execute(sql_content)

            self.stdout.write(self.style.SUCCESS('シードデータを投入しました'))
            self._show_data_counts()

        except Exception as e:
            self.stderr.write(
                self.style.ERROR(f'シードデータ投入中にエラー: {e}')
            )
            raise

    def _vectorize_all(self):
        """全データをベクトル化"""
        self.stdout.write(self.style.WARNING('\n3. データをベクトル化中...\n'))

        from reports.models import DailyReport
        from bbs.models import BBSPost, BBSComment
        from ai_features.services.core_services import VectorizationService

        # 日報のベクトル化
        self.stdout.write('  日報をベクトル化中...')
        reports = DailyReport.objects.all()
        success, fail = 0, 0

        for report in reports:
            if VectorizationService.vectorize_daily_report(report.report_id):
                success += 1
            else:
                fail += 1

        self.stdout.write(
            self.style.SUCCESS(f'    日報: 成功 {success}件, 失敗 {fail}件')
        )

        # BBS投稿のベクトル化
        self.stdout.write('  掲示板投稿をベクトル化中...')
        posts = BBSPost.objects.all()
        success, fail = 0, 0

        for post in posts:
            if VectorizationService.vectorize_bbs_post(post.post_id):
                success += 1
            else:
                fail += 1

        self.stdout.write(
            self.style.SUCCESS(f'    掲示板投稿: 成功 {success}件, 失敗 {fail}件')
        )

        # BBSコメントのベクトル化
        self.stdout.write('  掲示板コメントをベクトル化中...')
        comments = BBSComment.objects.all()
        success, fail = 0, 0

        for comment in comments:
            if VectorizationService.vectorize_bbs_comment(comment.comment_id):
                success += 1
            else:
                fail += 1

        self.stdout.write(
            self.style.SUCCESS(f'    掲示板コメント: 成功 {success}件, 失敗 {fail}件')
        )

    def _show_data_counts(self):
        """データ件数を表示"""
        tables = [
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

        self.stdout.write('\n  データ件数:')
        with connection.cursor() as cursor:
            for table_name, display_name in tables:
                try:
                    cursor.execute(f'SELECT COUNT(*) FROM {table_name}')
                    count = cursor.fetchone()[0]
                    self.stdout.write(f'    {display_name}: {count}件')
                except Exception:
                    pass

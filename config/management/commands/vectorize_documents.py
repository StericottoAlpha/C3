"""
ドキュメントをベクトル化するDjango管理コマンド

使用例:
    python manage.py vectorize_documents --all
    python manage.py vectorize_documents --daily-reports
    python manage.py vectorize_documents --bbs-posts
    python manage.py vectorize_documents --report-id 123
"""
from django.core.management.base import BaseCommand, CommandError
from django.db import transaction
from tqdm import tqdm

from ai_features.core_services import VectorizationService
from reports.models import DailyReport
from bbs.models import BBSPost, BBSComment


class Command(BaseCommand):
    help = 'ドキュメントをベクトル化してDocumentVectorテーブルに保存します'

    def add_arguments(self, parser):
        parser.add_argument(
            '--all',
            action='store_true',
            help='全てのドキュメント（日報、掲示板投稿、コメント）をベクトル化',
        )
        parser.add_argument(
            '--daily-reports',
            action='store_true',
            help='全ての日報をベクトル化',
        )
        parser.add_argument(
            '--bbs-posts',
            action='store_true',
            help='全ての掲示板投稿をベクトル化',
        )
        parser.add_argument(
            '--bbs-comments',
            action='store_true',
            help='全ての掲示板コメントをベクトル化',
        )
        parser.add_argument(
            '--report-id',
            type=int,
            help='特定の日報IDをベクトル化',
        )
        parser.add_argument(
            '--post-id',
            type=int,
            help='特定の掲示板投稿IDをベクトル化',
        )
        parser.add_argument(
            '--comment-id',
            type=int,
            help='特定の掲示板コメントIDをベクトル化',
        )

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('ベクトル化処理を開始します...\n'))

        # 特定のドキュメント処理
        if options['report_id']:
            self.vectorize_single_report(options['report_id'])
            return

        if options['post_id']:
            self.vectorize_single_post(options['post_id'])
            return

        if options['comment_id']:
            self.vectorize_single_comment(options['comment_id'])
            return

        # 一括処理
        if options['all']:
            self.vectorize_all_reports()
            self.vectorize_all_posts()
            self.vectorize_all_comments()
            return

        if options['daily_reports']:
            self.vectorize_all_reports()
            return

        if options['bbs_posts']:
            self.vectorize_all_posts()
            return

        if options['bbs_comments']:
            self.vectorize_all_comments()
            return

        # オプションが指定されていない場合
        raise CommandError(
            'オプションを指定してください。--help でヘルプを表示します。'
        )

    def vectorize_single_report(self, report_id):
        """特定の日報をベクトル化"""
        self.stdout.write(f'日報ID {report_id} をベクトル化中...')

        result = VectorizationService.vectorize_daily_report(report_id)

        if result:
            self.stdout.write(self.style.SUCCESS(f'✓ 日報ID {report_id} のベクトル化が完了しました'))
        else:
            self.stdout.write(self.style.ERROR(f'✗ 日報ID {report_id} のベクトル化に失敗しました'))

    def vectorize_single_post(self, post_id):
        """特定の掲示板投稿をベクトル化"""
        self.stdout.write(f'掲示板投稿ID {post_id} をベクトル化中...')

        result = VectorizationService.vectorize_bbs_post(post_id)

        if result:
            self.stdout.write(self.style.SUCCESS(f'✓ 掲示板投稿ID {post_id} のベクトル化が完了しました'))
        else:
            self.stdout.write(self.style.ERROR(f'✗ 掲示板投稿ID {post_id} のベクトル化に失敗しました'))

    def vectorize_single_comment(self, comment_id):
        """特定の掲示板コメントをベクトル化"""
        self.stdout.write(f'掲示板コメントID {comment_id} をベクトル化中...')

        result = VectorizationService.vectorize_bbs_comment(comment_id)

        if result:
            self.stdout.write(self.style.SUCCESS(f'✓ 掲示板コメントID {comment_id} のベクトル化が完了しました'))
        else:
            self.stdout.write(self.style.ERROR(f'✗ 掲示板コメントID {comment_id} のベクトル化に失敗しました'))

    def vectorize_all_reports(self):
        """全ての日報をベクトル化"""
        self.stdout.write(self.style.WARNING('\n=== 日報のベクトル化 ==='))

        reports = DailyReport.objects.all()
        total = reports.count()

        if total == 0:
            self.stdout.write('ベクトル化する日報がありません')
            return

        success_count = 0
        error_count = 0

        for report in tqdm(reports, desc='日報をベクトル化中', unit='件'):
            result = VectorizationService.vectorize_daily_report(report.report_id)
            if result:
                success_count += 1
            else:
                error_count += 1

        self.stdout.write(self.style.SUCCESS(
            f'\n日報のベクトル化完了: 成功 {success_count}件, 失敗 {error_count}件, 合計 {total}件'
        ))

    def vectorize_all_posts(self):
        """全ての掲示板投稿をベクトル化"""
        self.stdout.write(self.style.WARNING('\n=== 掲示板投稿のベクトル化 ==='))

        posts = BBSPost.objects.all()
        total = posts.count()

        if total == 0:
            self.stdout.write('ベクトル化する掲示板投稿がありません')
            return

        success_count = 0
        error_count = 0

        for post in tqdm(posts, desc='掲示板投稿をベクトル化中', unit='件'):
            result = VectorizationService.vectorize_bbs_post(post.post_id)
            if result:
                success_count += 1
            else:
                error_count += 1

        self.stdout.write(self.style.SUCCESS(
            f'\n掲示板投稿のベクトル化完了: 成功 {success_count}件, 失敗 {error_count}件, 合計 {total}件'
        ))

    def vectorize_all_comments(self):
        """全ての掲示板コメントをベクトル化"""
        self.stdout.write(self.style.WARNING('\n=== 掲示板コメントのベクトル化 ==='))

        comments = BBSComment.objects.all()
        total = comments.count()

        if total == 0:
            self.stdout.write('ベクトル化する掲示板コメントがありません')
            return

        success_count = 0
        error_count = 0

        for comment in tqdm(comments, desc='掲示板コメントをベクトル化中', unit='件'):
            result = VectorizationService.vectorize_bbs_comment(comment.comment_id)
            if result:
                success_count += 1
            else:
                error_count += 1

        self.stdout.write(self.style.SUCCESS(
            f'\n掲示板コメントのベクトル化完了: 成功 {success_count}件, 失敗 {error_count}件, 合計 {total}件'
        ))

from django.core.management.base import BaseCommand
from django.core.management import call_command
from django.contrib.auth import get_user_model
from django.utils import timezone
from stores.models import Store, MonthlyGoal
from reports.models import DailyReport, StoreDailyPerformance
from bbs.models import BBSPost, BBSComment, BBSReaction
from ai_features.models import AIProposal, AIAnalysisResult, AIChatHistory
from pathlib import Path
from datetime import datetime, timedelta
import glob

User = get_user_model()


class Command(BaseCommand):
    help = 'Seed database with initial data'

    def handle(self, *args, **options):
        self.stdout.write('Seeding database...')

        # 1. 店舗データ作成
        stores_data = [
            {'store_name': '本部', 'address': '東京都千代田区丸の内1-1-1'},
            {'store_name': 'A店', 'address': '東京都渋谷区道玄坂1-2-3'},
            {'store_name': 'B店', 'address': '大阪府大阪市北区梅田1-1-1'},
            {'store_name': 'C店', 'address': '愛知県名古屋市中区栄3-4-5'},
        ]

        stores = {}
        for store_data in stores_data:
            store, created = Store.objects.get_or_create(
                store_name=store_data['store_name'],
                defaults={
                    'address': store_data['address']
                }
            )
            stores[store_data['store_name']] = store
            if created:
                self.stdout.write(self.style.SUCCESS(f'Created store: {store.store_name}'))

# 2. ユーザーデータ作成
        users_data = [
            {'user_id': 'admin', 'last_name': 'システム', 'first_name': '管理者', 'store': '本部', 'user_type': 'admin', 'email': 'admin@example.com'},
            {'user_id': 'manager001', 'last_name': '佐藤', 'first_name': '健一', 'store': 'A店', 'user_type': 'manager', 'email': 'manager.a@example.com'},
            {'user_id': 'manager002', 'last_name': '鈴木', 'first_name': '一郎', 'store': 'B店', 'user_type': 'manager', 'email': 'manager.b@example.com'},
            {'user_id': 'staff001', 'last_name': '田中', 'first_name': '花子', 'store': 'A店', 'user_type': 'staff', 'email': 'staff001@example.com'},
            {'user_id': 'staff002', 'last_name': '高橋', 'first_name': '次郎', 'store': 'A店', 'user_type': 'staff', 'email': 'staff002@example.com'},
            {'user_id': 'staff003', 'last_name': '渡辺', 'first_name': '美咲', 'store': 'B店', 'user_type': 'staff', 'email': 'staff003@example.com'},
            {'user_id': 'staff004', 'last_name': '伊藤', 'first_name': '健太', 'store': 'C店', 'user_type': 'staff', 'email': 'staff004@example.com'},
        ]

        users = {}
        for user_data in users_data:
            if not User.objects.filter(user_id=user_data['user_id']).exists():
                user = User.objects.create_user(
                    user_id=user_data['user_id'],
                    password='password123',  # 全ユーザー共通パスワード（開発用）
                    last_name=user_data['last_name'],   # 追加
                    first_name=user_data['first_name'], # 追加
                    store=stores[user_data['store']],
                    user_type=user_data['user_type'],
                    email=user_data.get('email')
                )
                if user_data['user_type'] == 'admin':
                    user.is_staff = True
                    user.is_superuser = True
                    user.save()
                users[user_data['user_id']] = user
                self.stdout.write(self.style.SUCCESS(f'Created user: {user.user_id} ({user.last_name} {user.first_name})'))
            else:
                users[user_data['user_id']] = User.objects.get(user_id=user_data['user_id'])

        # 3. 店舗日次実績データ作成（過去30日分）
        today = datetime.now().date()
        for i in range(30):
            date = today - timedelta(days=i)
            for store in [stores['A店'], stores['B店'], stores['C店']]:
                if not StoreDailyPerformance.objects.filter(store=store, date=date).exists():
                    StoreDailyPerformance.objects.create(
                        store=store,
                        date=date,
                        sales_amount=300000 + (i * 10000) + (store.store_id * 50000),
                        customer_count=150 + (i * 5) + (store.store_id * 10),
                        cash_difference=(-100 if i % 7 == 0 else 0),  # 7日に1回違算
                        registered_by=users.get('manager001') if store.store_name == 'A店' else users.get('manager002')
                    )
        self.stdout.write(self.style.SUCCESS('Created 30 days of performance data for stores'))

        # 4. 日報データ作成（過去30日分）
        genres = ['claim', 'praise', 'accident', 'report', 'other']
        locations = ['kitchen', 'hall', 'cashier', 'toilet', 'other']

        reports = []
        for i in range(30):
            date = today - timedelta(days=i)
            # 各日に1〜3件のインシデントを作成
            num_incidents = (i % 3) + 1  # 1, 2, 3のサイクル

            for j in range(num_incidents):
                store = stores['A店'] if i % 2 == 0 else stores['B店']
                user = users['staff001'] if store == stores['A店'] else users['staff003']
                genre = genres[i % len(genres)]
                location = locations[j % len(locations)]

                if not DailyReport.objects.filter(store=store, date=date, title=f'{genre}の報告{i}-{j}').exists():
                    report = DailyReport.objects.create(
                        store=store,
                        user=user,
                        date=date,
                        genre=genre,
                        location=location,
                        title=f'{genre}の報告{i}-{j}',
                        content=f'{date}の{location}で発生した{genre}です。',
                        post_to_bbs=(j == 0)  # 最初の1件のみ掲示板に投稿
                    )
                    reports.append(report)

        self.stdout.write(self.style.SUCCESS(f'Created {len(reports)} daily reports'))

        # 5. 掲示板投稿データ作成（日報から自動投稿 + 直接投稿）
        bbs_posts = []
        for report in reports:
            if report.post_to_bbs:
                post = BBSPost.objects.create(
                    store=report.store,
                    user=report.user,
                    report=report,
                    title=report.title,
                    content=report.content,
                    comment_count=0
                )
                bbs_posts.append(post)

        # 直接投稿
        direct_posts_data = [
            {
                'store': stores['A店'], 'user': users['staff001'],
                'title': 'ピーク時の動線改善案',
                'content': 'ランチタイムの混雑緩和のため、テーブルレイアウトを変更してはどうでしょうか？',
            },
            {
                'store': stores['B店'], 'user': users['manager002'],
                'title': '新メニューのアイデア募集',
                'content': '来月から季節限定メニューを追加したいと思います。皆さんのアイデアをお聞かせください。',
            },
        ]

        for post_data in direct_posts_data:
            post = BBSPost.objects.create(**post_data)
            bbs_posts.append(post)

        self.stdout.write(self.style.SUCCESS(f'Created {len(bbs_posts)} BBS posts'))

        # 6. 掲示板コメントデータ作成
        if bbs_posts:
            BBSComment.objects.create(
                post=bbs_posts[0],
                user=users['manager001'],
                content='ご報告ありがとうございます。スタッフ配置の見直しを検討します。',
                is_best_answer=False
            )
            BBSComment.objects.create(
                post=bbs_posts[0],
                user=users['staff002'],
                content='私も同様の経験がありました。ピーク時は2名体制が良いと思います。',
                is_best_answer=True
            )
            self.stdout.write(self.style.SUCCESS('Created BBS comments'))

        # 7. 掲示板リアクションデータ作成
        if bbs_posts:
            BBSReaction.objects.create(
                post=bbs_posts[0],
                user=users['staff002'],
                reaction_type='naruhodo'
            )
            BBSReaction.objects.create(
                post=bbs_posts[0],
                user=users['manager001'],
                reaction_type='arigatou'
            )
            self.stdout.write(self.style.SUCCESS('Created BBS reactions'))

        # 8. AI改善提案データ作成
        AIProposal.objects.create(
            user=users['manager001'],
            priority=3,
            proposal_type='frequent_claim',
            content='過去1週間で「接客対応が遅い」というクレームが3件発生しています。ピーク時のスタッフ配置を見直すことをお勧めします。',
            is_read=False
        )
        AIProposal.objects.create(
            user=users['manager002'],
            priority=2,
            proposal_type='cash_difference',
            content='B店で違算が2回連続で発生しています。レジ締め手順の再確認をお勧めします。',
            is_read=False
        )
        self.stdout.write(self.style.SUCCESS('Created AI proposals'))

        # 9. AI分析結果データ作成
        AIAnalysisResult.objects.create(
            target_period='2024年12月1日 - 12月7日',
            analysis_type='weekly',
            analysis_result={
                'total_sales': 2100000,
                'average_customers': 850,
                'incident_count': {'claim': 3, 'praise': 2, 'accident': 1}
            },
            warning_points=['A店: 接客クレーム増加傾向', 'B店: 違算発生']
        )
        self.stdout.write(self.style.SUCCESS('Created AI analysis results'))

        # 10. AIチャット履歴データ作成
        AIChatHistory.objects.create(
            user=users['staff001'],
            role='user',
            message='フライヤーの適正温度は何度ですか？'
        )
        AIChatHistory.objects.create(
            user=users['staff001'],
            role='assistant',
            message='フライヤーの適正温度は一般的に170-180℃です。揚げ物の種類によって調整してください。'
        )
        self.stdout.write(self.style.SUCCESS('Created AI chat history'))

        # 11. 月次目標データ作成（今月と先月）
        today = datetime.now().date()
        current_year = today.year
        current_month = today.month

        # 今月の目標
        monthly_goals_data = [
            {
                'store': stores['A店'],
                'year': current_year,
                'month': current_month,
                'goal_text': 'クレーム5件以下！\n売上目標500万円達成！\n違算ゼロ！',
                'achievement_rate': 75,
                'achievement_text': '順調に進んでいます'
            },
            {
                'store': stores['B店'],
                'year': current_year,
                'month': current_month,
                'goal_text': '客数1000人以上！\nスタッフ全員で笑顔の接客！',
                'achievement_rate': 60,
                'achievement_text': 'もう少し頑張りましょう'
            },
            {
                'store': stores['C店'],
                'year': current_year,
                'month': current_month,
                'goal_text': '新メニュー販売数100個以上！\n顧客満足度向上！',
                'achievement_rate': 85,
                'achievement_text': '好調です！'
            },
        ]

        # 先月の目標（参考用）
        last_month = current_month - 1 if current_month > 1 else 12
        last_year = current_year if current_month > 1 else current_year - 1

        monthly_goals_data.extend([
            {
                'store': stores['A店'],
                'year': last_year,
                'month': last_month,
                'goal_text': 'クレーム3件以下！\n売上目標450万円達成！',
                'achievement_rate': 90,
                'achievement_text': '目標達成しました！'
            },
            {
                'store': stores['B店'],
                'year': last_year,
                'month': last_month,
                'goal_text': '客数900人以上！\n接客研修完了！',
                'achievement_rate': 95,
                'achievement_text': '素晴らしい成果です'
            },
        ])

        for goal_data in monthly_goals_data:
            MonthlyGoal.objects.get_or_create(
                store=goal_data['store'],
                year=goal_data['year'],
                month=goal_data['month'],
                defaults={
                    'goal_text': goal_data['goal_text'],
                    'achievement_rate': goal_data['achievement_rate'],
                    'achievement_text': goal_data['achievement_text']
                }
            )

        self.stdout.write(self.style.SUCCESS('Created monthly goals'))

        # Load seed data from JSON files
        fixtures_dir = Path(__file__).resolve().parent.parent.parent / 'fixtures'
        if fixtures_dir.exists():
            seed_files = sorted(glob.glob(str(fixtures_dir / 'seed_*.json')))
            for seed_file in seed_files:
                filename = Path(seed_file).name
                self.stdout.write(f'Loading fixture: {filename}')
                try:
                    call_command('loaddata', seed_file, verbosity=0)
                    self.stdout.write(self.style.SUCCESS(f'  ✓ Loaded {filename}'))
                except Exception as e:
                    self.stdout.write(self.style.ERROR(f'  ✗ Failed to load {filename}: {e}'))
        else:
            self.stdout.write(self.style.WARNING(f'Fixtures directory not found: {fixtures_dir}'))

        self.stdout.write(self.style.SUCCESS('Database seeded successfully!'))

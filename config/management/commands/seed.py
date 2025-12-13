from django.core.management.base import BaseCommand
from django.core.management import call_command
from django.contrib.auth import get_user_model
from django.utils import timezone
from stores.models import Store
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
            {'store_name': '本部', 'address': '東京都千代田区丸の内1-1-1', 'sales_target': '月間売上目標: 1000万円'},
            {'store_name': 'A店', 'address': '東京都渋谷区道玄坂1-2-3', 'sales_target': '月間売上目標: 500万円'},
            {'store_name': 'B店', 'address': '大阪府大阪市北区梅田1-1-1', 'sales_target': '月間売上目標: 600万円'},
            {'store_name': 'C店', 'address': '愛知県名古屋市中区栄3-4-5', 'sales_target': '月間売上目標: 450万円'},
        ]

        stores = {}
        for store_data in stores_data:
            store, created = Store.objects.get_or_create(
                store_name=store_data['store_name'],
                defaults={
                    'address': store_data['address'],
                    'sales_target': store_data['sales_target']
                }
            )
            stores[store_data['store_name']] = store
            if created:
                self.stdout.write(self.style.SUCCESS(f'Created store: {store.store_name}'))

        # 2. ユーザーデータ作成
        users_data = [
            {'user_id': 'admin', 'store': '本部', 'user_type': 'admin', 'email': 'admin@example.com'},
            {'user_id': 'manager001', 'store': 'A店', 'user_type': 'manager', 'email': 'manager.a@example.com'},
            {'user_id': 'manager002', 'store': 'B店', 'user_type': 'manager', 'email': 'manager.b@example.com'},
            {'user_id': 'staff001', 'store': 'A店', 'user_type': 'staff', 'email': 'staff001@example.com'},
            {'user_id': 'staff002', 'store': 'A店', 'user_type': 'staff', 'email': 'staff002@example.com'},
            {'user_id': 'staff003', 'store': 'B店', 'user_type': 'staff', 'email': 'staff003@example.com'},
            {'user_id': 'staff004', 'store': 'C店', 'user_type': 'staff', 'email': 'staff004@example.com'},
        ]

        users = {}
        for user_data in users_data:
            if not User.objects.filter(user_id=user_data['user_id']).exists():
                user = User.objects.create_user(
                    user_id=user_data['user_id'],
                    password='password123',  # 全ユーザー共通パスワード（開発用）
                    store=stores[user_data['store']],
                    user_type=user_data['user_type'],
                    email=user_data.get('email')
                )
                if user_data['user_type'] == 'admin':
                    user.is_staff = True
                    user.is_superuser = True
                    user.save()
                users[user_data['user_id']] = user
                self.stdout.write(self.style.SUCCESS(f'Created user: {user.user_id} ({user.get_user_type_display()})'))
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

        # 4. 日報データ作成（多様なシナリオ）
        reports_data = [
            # A店のデータ（接客・クレーム中心）
            {
                'store': stores['A店'], 'user': users['staff001'], 'date': today,
                'genre': 'claim', 'location': 'hall', 'title': '接客態度に関するクレーム',
                'content': 'お客様から「スタッフの対応が遅い」とのご指摘をいただきました。ピーク時の対応について改善が必要です。レジ待ち時間が10分以上かかり、お客様を不快にさせてしまいました。',
                'post_to_bbs': True
            },
            {
                'store': stores['A店'], 'user': users['staff002'], 'date': today - timedelta(days=1),
                'genre': 'praise', 'location': 'kitchen', 'title': '料理の美味しさを褒められました',
                'content': 'お客様から「今日のハンバーグは特に美味しかった」と直接お褒めの言葉をいただきました。シェフの丁寧な調理が評価されています。',
                'post_to_bbs': True
            },
            {
                'store': stores['A店'], 'user': users['staff001'], 'date': today - timedelta(days=2),
                'genre': 'claim', 'location': 'hall', 'title': '料理提供の遅延',
                'content': 'ランチタイムに注文から提供まで25分かかってしまいました。お客様から「遅すぎる」とお叱りを受けました。キッチンとホールの連携を改善する必要があります。',
                'post_to_bbs': True
            },
            {
                'store': stores['A店'], 'user': users['staff002'], 'date': today - timedelta(days=3),
                'genre': 'praise', 'location': 'hall', 'title': '子連れ対応を褒められました',
                'content': '小さなお子様連れのお客様から「スタッフの気配りが素晴らしかった」とお褒めの言葉をいただきました。子供用の食器やクレヨンを用意したことが好評でした。',
                'post_to_bbs': True
            },
            {
                'store': stores['A店'], 'user': users['staff001'], 'date': today - timedelta(days=5),
                'genre': 'claim', 'location': 'kitchen', 'title': '料理の温度が低い',
                'content': 'お客様から「スープがぬるかった」とご指摘を受けました。再加熱してお出ししましたが、提供前の温度確認を徹底する必要があります。',
                'post_to_bbs': True
            },
            {
                'store': stores['A店'], 'user': users['staff002'], 'date': today - timedelta(days=7),
                'genre': 'report', 'location': 'hall', 'title': '売上好調',
                'content': '本日の売上が過去最高の38万円を記録しました。新メニューのカレーが好評で、注文が集中しました。',
                'post_to_bbs': True
            },

            # B店のデータ（設備トラブル・事故中心）
            {
                'store': stores['B店'], 'user': users['staff003'], 'date': today,
                'genre': 'accident', 'location': 'kitchen', 'title': 'フライヤーの点検',
                'content': 'フライヤーの温度が不安定だったため、業者に連絡して点検を依頼しました。温度計の故障が原因でした。',
                'post_to_bbs': False
            },
            {
                'store': stores['B店'], 'user': users['staff003'], 'date': today - timedelta(days=1),
                'genre': 'accident', 'location': 'hall', 'title': '食器の破損事故',
                'content': 'スタッフが食器を運搬中にお皿を2枚落として破損しました。けが人はありませんでしたが、再発防止のためトレーの使用を徹底します。',
                'post_to_bbs': True
            },
            {
                'store': stores['B店'], 'user': users['manager002'], 'date': today - timedelta(days=2),
                'genre': 'report', 'location': 'toilet', 'title': 'トイレ清掃の改善',
                'content': '本日よりトイレ清掃チェックリストを導入しました。30分おきの確認を徹底します。お客様から「トイレが清潔」と好評です。',
                'post_to_bbs': True
            },
            {
                'store': stores['B店'], 'user': users['staff003'], 'date': today - timedelta(days=3),
                'genre': 'claim', 'location': 'cashier', 'title': 'レジの金額相違',
                'content': 'お客様からお会計の金額が違うとご指摘を受けました。レジの入力ミスでした。確認を怠らないよう注意します。',
                'post_to_bbs': True
            },
            {
                'store': stores['B店'], 'user': users['staff003'], 'date': today - timedelta(days=4),
                'genre': 'accident', 'location': 'kitchen', 'title': '冷蔵庫の温度異常',
                'content': '冷蔵庫の温度が10度まで上昇していることに気づきました。食材の廃棄を行い、修理業者を手配しました。損失額は約3万円です。',
                'post_to_bbs': True
            },
            {
                'store': stores['B店'], 'user': users['manager002'], 'date': today - timedelta(days=6),
                'genre': 'report', 'location': 'other', 'title': '新人スタッフの育成',
                'content': '新人スタッフの山田さんが接客に慣れてきました。本日から一人でホール業務を担当してもらいます。',
                'post_to_bbs': True
            },

            # C店のデータ（バランス型）
            {
                'store': stores['C店'], 'user': users['staff004'], 'date': today,
                'genre': 'praise', 'location': 'hall', 'title': '常連客からの感謝',
                'content': '常連のお客様から「いつも笑顔で迎えてくれてありがとう」と温かいお言葉をいただきました。スタッフ一同励みになります。',
                'post_to_bbs': True
            },
            {
                'store': stores['C店'], 'user': users['staff004'], 'date': today - timedelta(days=1),
                'genre': 'report', 'location': 'kitchen', 'title': '食材在庫の適正化',
                'content': '野菜の発注量を調整し、廃棄ロスを削減できました。先週比で廃棄量が30%減少しています。',
                'post_to_bbs': True
            },
            {
                'store': stores['C店'], 'user': users['staff004'], 'date': today - timedelta(days=3),
                'genre': 'claim', 'location': 'hall', 'title': '席の案内ミス',
                'content': 'お客様を予約席ではない席にご案内してしまい、ご迷惑をおかけしました。予約確認を徹底します。',
                'post_to_bbs': True
            },
            {
                'store': stores['C店'], 'user': users['staff004'], 'date': today - timedelta(days=5),
                'genre': 'praise', 'location': 'kitchen', 'title': '季節メニューが好評',
                'content': '新しく追加した秋の限定メニュー「栗のモンブランパフェ」が大変好評で、1日20個以上売れています。',
                'post_to_bbs': True
            },
            {
                'store': stores['C店'], 'user': users['staff004'], 'date': today - timedelta(days=7),
                'genre': 'report', 'location': 'other', 'title': '省エネ対策の実施',
                'content': '照明をLEDに変更し、電気代の削減を実現しました。月間約1万円のコスト削減が見込まれます。',
                'post_to_bbs': True
            },
        ]

        reports = []
        for report_data in reports_data:
            report = DailyReport.objects.create(**report_data)
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

        # 直接投稿（より多様なトピック）
        direct_posts_data = [
            {
                'store': stores['A店'], 'user': users['staff001'],
                'title': 'ピーク時の動線改善案',
                'content': 'ランチタイムの混雑緩和のため、テーブルレイアウトを変更してはどうでしょうか？入口から奥に向かう一方通行の動線を作ることで、お客様の流れがスムーズになると思います。',
            },
            {
                'store': stores['B店'], 'user': users['manager002'],
                'title': '新メニューのアイデア募集',
                'content': '来月から季節限定メニューを追加したいと思います。皆さんのアイデアをお聞かせください。冬に人気が出そうな温かい料理を考えています。',
            },
            {
                'store': stores['A店'], 'user': users['manager001'],
                'title': 'クレーム対応の共有',
                'content': '最近、接客スピードに関するクレームが増えています。皆さんの経験と対策を共有してください。特にピーク時の効率的な動き方について意見交換したいです。',
            },
            {
                'store': stores['B店'], 'user': users['staff003'],
                'title': '設備メンテナンスの記録',
                'content': '厨房機器の定期メンテナンスについて、今後は月次でチェックシートを作成して記録を残すようにしましょう。フライヤーやオーブンの調子が悪くなる前に予防できます。',
            },
            {
                'store': stores['C店'], 'user': users['staff004'],
                'title': 'お客様の声を共有',
                'content': '常連のお客様から「最近サービスが良くなった」とのお声をいただきました。みんなで頑張った成果が出ていますね！この調子で続けていきましょう。',
            },
            {
                'store': stores['A店'], 'user': users['staff002'],
                'title': '新人研修マニュアルの提案',
                'content': '新しく入るスタッフのために、写真付きの研修マニュアルを作成してはどうでしょうか？レジ操作や調理手順を視覚的に説明できると教育が効率的になると思います。',
            },
        ]

        for post_data in direct_posts_data:
            post = BBSPost.objects.create(**post_data)
            bbs_posts.append(post)

        self.stdout.write(self.style.SUCCESS(f'Created {len(bbs_posts)} BBS posts'))

        # 6. 掲示板コメントデータ作成（より多様なコメント）
        if len(bbs_posts) >= 3:
            # 最初の投稿（クレーム関連）へのコメント
            BBSComment.objects.create(
                post=bbs_posts[0],
                user=users['manager001'],
                content='ご報告ありがとうございます。スタッフ配置の見直しを検討します。ピーク時は最低2名体制にします。',
                is_best_answer=False
            )
            BBSComment.objects.create(
                post=bbs_posts[0],
                user=users['staff002'],
                content='私も同様の経験がありました。ピーク時は2名体制が良いと思います。あと、レジ前の待機スペースを確保すると良いかもしれません。',
                is_best_answer=True
            )

            # 2番目の投稿へのコメント
            if len(bbs_posts) > 1:
                BBSComment.objects.create(
                    post=bbs_posts[1],
                    user=users['manager001'],
                    content='素晴らしい報告ですね！料理の品質を保つことは最も重要です。引き続きよろしくお願いします。',
                    is_best_answer=False
                )

            # 3番目の投稿へのコメント
            if len(bbs_posts) > 2:
                BBSComment.objects.create(
                    post=bbs_posts[2],
                    user=users['manager001'],
                    content='提供時間の改善は急務ですね。キッチンとの連携について明日ミーティングを開きましょう。',
                    is_best_answer=False
                )
                BBSComment.objects.create(
                    post=bbs_posts[2],
                    user=users['staff002'],
                    content='注文票の書き方を統一すると、キッチンも調理の優先順位がわかりやすくなると思います。',
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

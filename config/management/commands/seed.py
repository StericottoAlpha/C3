import random
from django.core.management.base import BaseCommand
from django.core.management import call_command
from django.contrib.auth import get_user_model
from django.utils import timezone
from stores.models import Store, MonthlyGoal
from reports.models import DailyReport, StoreDailyPerformance
from bbs.models import BBSPost, BBSComment, BBSReaction
from ai_features.models import  AIChatHistory
from pathlib import Path
from datetime import datetime, timedelta
from ai_features.services.core_services import VectorizationService
from tqdm import tqdm
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

        # 4. 日報データ作成（ランダム大量生成版）
        self.stdout.write(self.style.WARNING('\n=== 日報データの大量生成を開始します ==='))

        # 生成する日報の件数（ここを変更すれば好きなだけ増やせます）
        NUM_REPORTS_TO_GENERATE = 300

        # 店舗とスタッフのマッピング
        store_staff_map = {
            'A店': ['manager001', 'staff001', 'staff002'],
            'B店': ['manager002', 'staff003'],
            'C店': ['staff004']
        }

        # テンプレートデータの定義
        templates = {
            'claim': [
                ('hall', '接客態度への指摘', 'お客様より「スタッフの笑顔がない」「元気が足りない」とのご指摘をいただきました。疲れていても表に出さないよう、プロ意識の指導が必要です。'),
                ('hall', '提供遅れ', 'ランチピーク時に料理の提供まで25分以上かかり、お叱りを受けました。ホールの連携ミスとキッチンの遅延が重なったことが原因です。'),
                ('hall', '注文間違い', 'オーダーミスにより違う商品を提供してしまいました。ハンディの入力確認と復唱確認を徹底します。'),
                ('hall', '席への案内遅れ', '空席があるのに入り口で待たされたとクレームがありました。バッシングの優先順位を見直す必要があります。'),
                ('kitchen', '料理の異物混入', 'サラダにビニール片が混入していたと報告がありました。食材開封時の確認プロセスを強化します。'),
                ('kitchen', '料理が冷めている', '提供されたスープがぬるいとの指摘を受けました。パッサーでの滞留時間が長かった可能性があります。'),
                ('kitchen', '味付けの不備', '「今日のパスタは塩辛い」とのご意見をいただきました。調理マニュアルの分量を再確認させました。'),
                ('cashier', '会計ミス', '釣り銭の渡し間違いが発生しました。お客様が帰宅後に電話で判明し、謝罪対応を行いました。'),
            ],
            'praise': [
                ('hall', '笑顔での接客', '「担当スタッフの笑顔が素敵で癒やされた」と直接お褒めの言葉をいただきました。'),
                ('hall', '気配りへの感謝', 'お水を注ぐタイミングが絶妙だったと感謝されました。「よく見ているね」と言っていただけました。'),
                ('hall', '子供への対応', 'お子様連れのお客様より、子供用の椅子や取り皿をすぐに用意したことを褒められました。'),
                ('kitchen', '料理の味', '「今まで食べたハンバーグで一番美味しい」と絶賛されました。シェフに共有し、モチベーションアップに繋げます。'),
                ('kitchen', '提供スピード', '急いでいるお客様への提供が早く、「助かった、ありがとう」と感謝されました。'),
                ('other', '店内の清掃', 'トイレや洗面台が非常に綺麗で気持ちが良いとお褒めいただきました。清掃スタッフの努力の成果です。'),
            ],
            'accident': [
                ('hall', '食器の破損', 'バッシング中にグラスを落として割ってしまいました。破片の処理は完了し、怪我人はありませんでした。'),
                ('hall', 'お客様との接触', '配膳中にお客様とぶつかりそうになりました。「後ろを通ります」の声掛けをより大きな声で徹底します。'),
                ('hall', 'ドリンク転倒', 'テーブルにお水をこぼしてしまいました。お客様の服にはかかりませんでしたが、謝罪し新しいおしぼりを提供しました。'),
                ('kitchen', '指の切り傷', '仕込み中に包丁で指を軽く切ってしまいました。絆創膏で処置し、手袋を着用して作業を継続しています。'),
                ('kitchen', '火傷', 'オーブンの鉄板に腕が触れて軽い火傷をしました。注意散漫になっていたことが原因です。'),
                ('kitchen', '床の滑り', '油で床が滑りやすくなっており、転倒しそうになりました。すぐにデッキブラシで清掃を実施しました。'),
            ],
            'trouble': [
                ('kitchen', '食洗機の不調', '食洗機から異音がしています。一時的に手洗いで対応中です。業者手配済みです。'),
                ('kitchen', '冷蔵庫の温度', '冷蔵庫の温度が設定より少し高くなっています。フィルター掃除を実施して様子を見ています。'),
                ('hall', 'エアコンの水漏れ', 'エアコンから水が垂れてきました。真下の席を使用禁止にして対応しています。'),
                ('cashier', 'レジプリンター詰まり', 'レシート用紙が詰まって交換に時間を要しました。予備のロール紙の位置も再確認しました。'),
                ('kitchen', 'フライヤーの温度異常', 'フライヤーの温度が上がりにくい現象が発生しています。ピーク前に調整が必要です。'),
            ],
            'report': [
                ('other', '備品の発注', '洗剤とペーパータオルの在庫が少なくなったため発注完了しました。納品は明後日予定です。'),
                ('other', 'シフト調整', '来月のシフト希望を回収中です。週末の人員確保が少し厳しそうです。'),
                ('other', '新人の様子', '新人スタッフがメニューを覚え始めました。来週からオーダー取りを練習させる予定です。'),
                ('hall', 'メニューブックの補修', '破れかけているメニューブックをテープで補修しました。見栄えが悪いため、交換時期かもしれません。'),
                ('kitchen', '棚卸し実施', '月末の棚卸しを実施しました。大きな差異はありませんでした。'),
                ('hall', '売上目標達成', '本日のランチ売上が目標を達成しました。回転率が良く、スムーズな営業でした。'),
            ]
        }

        # 発生確率の重み付け (claim, praise, accident, trouble, report)
        genre_weights = [0.2, 0.3, 0.1, 0.1, 0.3]
        genres = ['claim', 'praise', 'accident', 'trouble', 'report']

        # 過去60日分からランダムに日付を生成
        base_date = datetime.now().date()
        generated_reports_data = []

        for _ in range(NUM_REPORTS_TO_GENERATE):
            # 1. 店舗をランダムに決定
            store_name = random.choice(list(store_staff_map.keys()))
            store_obj = stores[store_name]

            # 2. その店舗のスタッフをランダムに決定
            user_id = random.choice(store_staff_map[store_name])
            user_obj = users.get(user_id)

            # ユーザーが存在しない場合（seedデータの設定漏れ対策）はスキップ
            if not user_obj:
                continue

            # 3. 日付をランダムに決定（直近60日以内）
            days_ago = random.randint(0, 60)
            report_date = base_date - timedelta(days=days_ago)

            # 4. ジャンルを重み付けランダムで決定
            chosen_genre = random.choices(genres, weights=genre_weights, k=1)[0]

            # troubleキーがない場合はaccidentに倒すなどの調整（念のため）
            if chosen_genre == 'trouble' and 'trouble' not in templates:
                chosen_genre = 'accident'

            # 5. テンプレートからランダムに選択
            tpl = random.choice(templates[chosen_genre])
            location = tpl[0]
            title = tpl[1]
            base_content = tpl[2]

            # 内容に少しランダム性を加える（文末を変える）
            suffixes = ['', ' 今後気をつけます。', ' 共有お願いします。', ' 対応完了しました。', ' 早急に対策が必要です。', ' 引き続き注視します。']
            final_content = base_content + random.choice(suffixes)

            # 6. データ辞書作成
            generated_reports_data.append({
                'store': store_obj,
                'user': user_obj,
                'date': report_date,
                'genre': chosen_genre,
                'location': location,
                'title': title,
                'content': final_content,
                'post_to_bbs': random.choice([True, True, False])  # 2/3の確率で掲示板投稿
            })

        # 日付順にソート
        generated_reports_data.sort(key=lambda x: x['date'])

        # データベースへ登録
        reports = []
        for report_data in generated_reports_data:
            report = DailyReport.objects.create(**report_data)
            reports.append(report)
        self.stdout.write(self.style.SUCCESS(f'Created {len(reports)} daily reports (Randomly Generated)'))

        """全ての日報をベクトル化"""
        self.stdout.write(self.style.WARNING('\n=== 日報のベクトル化 ==='))

        # 生成したreportsリストではなく、DBから全件取得してベクトル化（以前のデータが残っている場合も考慮）
        target_reports = DailyReport.objects.all()
        total = target_reports.count()

        if total == 0:
            self.stdout.write('ベクトル化する日報がありません')
        else:
            success_count = 0
            error_count = 0

            for report in tqdm(target_reports, desc='日報をベクトル化中', unit='件'):
                result = VectorizationService.vectorize_daily_report(report.report_id)
                if result:
                    success_count += 1
                else:
                    error_count += 1

            self.stdout.write(self.style.SUCCESS(
                f'\n日報のベクトル化完了: 成功 {success_count}件, 失敗 {error_count}件, 合計 {total}件'
            ))

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
                'genre': 'claim',
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

        # 6. 掲示板コメントデータ作成
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

        """全てのBBS投稿とコメントをベクトル化"""
        self.stdout.write(self.style.WARNING('\n=== 掲示板投稿のベクトル化 ==='))

        # BBS投稿のベクトル化
        all_posts = BBSPost.objects.all()
        total_posts = all_posts.count()

        if total_posts > 0:
            success_count = 0
            error_count = 0

            for post in tqdm(all_posts, desc='掲示板投稿をベクトル化中', unit='件'):
                result = VectorizationService.vectorize_bbs_post(post.post_id)
                if result:
                    success_count += 1
                else:
                    error_count += 1

            self.stdout.write(self.style.SUCCESS(
                f'\n掲示板投稿のベクトル化完了: 成功 {success_count}件, 失敗 {error_count}件, 合計 {total_posts}件'
            ))
        else:
            self.stdout.write('ベクトル化する掲示板投稿がありません')

        # BBSコメントのベクトル化
        self.stdout.write(self.style.WARNING('\n=== 掲示板コメントのベクトル化 ==='))

        all_comments = BBSComment.objects.all()
        total_comments = all_comments.count()

        if total_comments > 0:
            success_count = 0
            error_count = 0

            for comment in tqdm(all_comments, desc='掲示板コメントをベクトル化中', unit='件'):
                result = VectorizationService.vectorize_bbs_comment(comment.comment_id)
                if result:
                    success_count += 1
                else:
                    error_count += 1

            self.stdout.write(self.style.SUCCESS(
                f'\n掲示板コメントのベクトル化完了: 成功 {success_count}件, 失敗 {error_count}件, 合計 {total_comments}件'
            ))
        else:
            self.stdout.write('ベクトル化する掲示板コメントがありません')

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

        

        # # 9. AI分析結果データ作成
        # AIAnalysisResult.objects.create(
        #     target_period='2024年12月1日 - 12月7日',
        #     analysis_type='weekly',
        #     analysis_result={
        #         'total_sales': 2100000,
        #         'average_customers': 850,
        #         'incident_count': {'claim': 3, 'praise': 2, 'accident': 1}
        #     },
        #     warning_points=['A店: 接客クレーム増加傾向', 'B店: 違算発生']
        # )
        # self.stdout.write(self.style.SUCCESS('Created AI analysis results'))

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

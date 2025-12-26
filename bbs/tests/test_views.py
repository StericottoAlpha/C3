import json
from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model
from bbs.models import BBSPost, BBSComment, BBSReaction
from stores.models import Store

User = get_user_model()

class BBSViewTests(TestCase):
    def setUp(self):
        """テスト前の準備"""
        # 1. 店舗の作成
        self.store = Store.objects.create(store_name="テスト店舗", store_id=1)

        # 2. ユーザーの作成 (username引数なし版)
        self.user = User.objects.create_user(
            password='password123',
            user_id='user001',
            store=self.store
        )
        # ログイン状態にする
        self.client.force_login(self.user)

        # 3. テスト用データの作成
        self.post1 = BBSPost.objects.create(
            user=self.user,
            store=self.store,
            title="美味しいラーメン",
            content="スープが最高でした",
            genre="praise"
        )
        
        self.post2 = BBSPost.objects.create(
            user=self.user,
            store=self.store,
            title="床が滑る",
            content="入り口付近で転倒しそうになった",
            genre="accident"
        )

    def test_bbs_list_access(self):
        """一覧画面が正常に開けるか"""
        response = self.client.get(reverse('bbs:list'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "美味しいラーメン")
        self.assertContains(response, "床が滑る")

    def test_genre_filter(self):
        """ジャンル絞り込み機能のテスト"""
        # accident で絞り込み
        response = self.client.get(reverse('bbs:list'), {'genre': 'accident'})
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "床が滑る")
        self.assertNotContains(response, "美味しいラーメン")

    def test_search_or_logic(self):
        """複数キーワード検索（OR検索）のテスト"""
        # 「ラーメン」または「滑る」
        response = self.client.get(reverse('bbs:list'), {'query': 'ラーメン　滑る'})
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "美味しいラーメン")
        self.assertContains(response, "床が滑る")

    def test_bbs_detail_access(self):
        """詳細画面のアクセステスト"""
        response = self.client.get(reverse('bbs:detail', args=[self.post1.post_id]))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "美味しいラーメン")

    def test_bbs_register_post(self):
        """新規投稿機能のテスト"""
        data = {
            'title': '新しいクレーム',
            'content': '商品が入っていなかった',
            'genre': 'claim',
            # reportフィールドは任意なので省略
        }
        # POSTリクエスト
        response = self.client.post(reverse('bbs:register'), data)
        
        # 投稿後は一覧へリダイレクト(302)するはず
        self.assertRedirects(response, reverse('bbs:list'))
        
        # データがDBに保存されたか確認
        self.assertTrue(BBSPost.objects.filter(title='新しいクレーム').exists())

    def test_bbs_comment_post(self):
        """コメント投稿機能のテスト"""
        data = {
            'content': 'テストコメントです',
        }
        url = reverse('bbs:comment', args=[self.post1.post_id])
        response = self.client.post(url, data)

        # 投稿後は詳細画面へリダイレクト(302)するはず
        self.assertRedirects(response, reverse('bbs:detail', args=[self.post1.post_id]))
        
        # コメントが保存されたか確認
        self.assertTrue(BBSComment.objects.filter(content='テストコメントです').exists())

    def test_toggle_reaction_post(self):
        """リアクション（いいね）の切り替えテスト"""
        url = reverse('bbs:toggle_reaction')
        data = {
            'target_type': 'post',
            'target_id': self.post1.post_id,
            'reaction_type': 'iine'
        }
        
        # 1回目：リアクション追加
        response = self.client.post(
            url,
            data=json.dumps(data),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 200)
        json_resp = response.json()
        self.assertEqual(json_resp['status'], 'success')
        self.assertEqual(json_resp['action'], 'added')
        self.assertEqual(json_resp['count'], 1)

        # 2回目：リアクション削除（トグル）
        response = self.client.post(
            url,
            data=json.dumps(data),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 200)
        json_resp = response.json()
        self.assertEqual(json_resp['status'], 'success')
        self.assertEqual(json_resp['action'], 'removed')
        self.assertEqual(json_resp['count'], 0)
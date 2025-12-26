from django.test import TestCase
from django.contrib.auth import get_user_model
from django.db.utils import IntegrityError
from django.db import transaction  # ▼▼▼ 追加 ▼▼▼
from bbs.models import BBSPost, BBSComment, BBSReaction, BBSCommentReaction
from stores.models import Store

User = get_user_model()

class BBSModelTests(TestCase):
    def setUp(self):
        """テスト前の準備：ユーザーと店舗を作成"""
        # 店舗作成
        self.store = Store.objects.create(store_name="テスト店舗", store_id=1)
        
        # ユーザー作成
        self.user = User.objects.create_user(
            password='password123',
            user_id='user001',
            store=self.store
        )

    def test_create_bbs_post(self):
        """投稿モデルの作成テスト"""
        post = BBSPost.objects.create(
            user=self.user,
            store=self.store,
            title="テスト投稿",
            content="これはテストです",
            genre="claim" # クレーム
        )
        # DBに保存されたか確認
        self.assertEqual(BBSPost.objects.count(), 1)
        self.assertEqual(post.title, "テスト投稿")
        self.assertEqual(post.genre, "claim")
        
        # __str__ メソッドのテスト
        expected_str = f"テスト投稿 - {self.user}"
        self.assertEqual(str(post), expected_str)

    def test_create_bbs_comment(self):
        """コメントモデルの作成テスト"""
        post = BBSPost.objects.create(
            user=self.user,
            store=self.store,
            title="親投稿",
            content="コメント用",
            genre="report"
        )
        comment = BBSComment.objects.create(
            post=post,
            user=self.user,
            content="テストコメント"
        )
        
        self.assertEqual(BBSComment.objects.count(), 1)
        self.assertEqual(comment.content, "テストコメント")
        
        # __str__ メソッドのテスト
        expected_str = f"Comment by {self.user} on 親投稿"
        self.assertEqual(str(comment), expected_str)

    def test_bbs_reaction_unique_constraint(self):
        """投稿リアクションの重複禁止テスト"""
        post = BBSPost.objects.create(
            user=self.user,
            store=self.store,
            title="リアクション用",
            content="...",
            genre="praise"
        )
        
        # 1回目のリアクション（いいね）
        BBSReaction.objects.create(
            post=post,
            user=self.user,
            reaction_type="iine"
        )
        
        # 2回目の同じリアクション（いいね） -> エラーになるべき
        with self.assertRaises(IntegrityError):
            # ▼▼▼ 修正: atomicで囲んでトランザクション破損を防ぐ ▼▼▼
            with transaction.atomic():
                BBSReaction.objects.create(
                    post=post,
                    user=self.user,
                    reaction_type="iine"
                )

        # 別の種類（なるほど）ならOK
        # ※ここでの操作を可能にするために上のatomicが必要です
        BBSReaction.objects.create(
            post=post,
            user=self.user,
            reaction_type="naruhodo"
        )
        self.assertEqual(BBSReaction.objects.count(), 2)

    def test_bbs_comment_reaction_unique_constraint(self):
        """コメントリアクションの重複禁止テスト"""
        post = BBSPost.objects.create(
            user=self.user,
            store=self.store,
            title="親投稿",
            content="...",
            genre="report"
        )
        comment = BBSComment.objects.create(
            post=post,
            user=self.user,
            content="テストコメント"
        )
        
        # 1回目のリアクション（いいね）
        BBSCommentReaction.objects.create(
            comment=comment,
            user=self.user,
            reaction_type="iine"
        )
        
        # 2回目の同じリアクション -> エラーになるべき
        with self.assertRaises(IntegrityError):
            # ▼▼▼ 修正: atomicで囲んでトランザクション破損を防ぐ ▼▼▼
            with transaction.atomic():
                BBSCommentReaction.objects.create(
                    comment=comment,
                    user=self.user,
                    reaction_type="iine"
                )
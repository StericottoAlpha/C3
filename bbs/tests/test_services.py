from django.test import TestCase
from django.contrib.auth import get_user_model
from unittest.mock import patch
from bbs.services import BBSService
from bbs.models import BBSPost, BBSComment
from stores.models import Store

User = get_user_model()

class BBSServiceTests(TestCase):
    def setUp(self):
        """テスト前の準備"""
        # 店舗作成
        self.store = Store.objects.create(store_name="テスト店舗", store_id=1)
        
        # ユーザー作成（username引数は使用しない）
        self.user = User.objects.create_user(
            password='password123',
            user_id='user001',
            store=self.store
        )

    # ▼▼▼ @patchでベクトル化機能を無効化（モック化）します ▼▼▼
    @patch('ai_features.services.core_services.VectorizationService.vectorize_bbs_post')
    def test_create_post(self, mock_vectorize):
        """投稿作成のテスト（ベクトル化呼び出し確認）"""
        # モックの戻り値を設定（True = 成功）
        mock_vectorize.return_value = True

        title = "サービス経由の投稿"
        content = "内容です"
        genre = "praise"

        # サービスの実行
        post = BBSService.create_post(
            store=self.store,
            user=self.user,
            title=title,
            content=content,
            genre=genre
        )

        # 1. DBに保存されたか確認
        self.assertEqual(BBSPost.objects.count(), 1)
        self.assertEqual(post.title, title)
        self.assertEqual(post.genre, genre)

        # 2. ベクトル化処理が「1回呼ばれたか」確認
        mock_vectorize.assert_called_once_with(post.post_id)

    @patch('ai_features.services.core_services.VectorizationService.vectorize_bbs_post')
    def test_update_post(self, mock_vectorize):
        """投稿更新のテスト"""
        mock_vectorize.return_value = True

        # 元の投稿を作成
        post = BBSPost.objects.create(
            store=self.store,
            user=self.user,
            title="古いタイトル",
            content="古い内容",
            genre="claim"
        )

        # 更新内容
        update_fields = {
            'title': '新しいタイトル',
            'genre': 'report'
        }

        # サービスの実行
        updated_post = BBSService.update_post(post, update_fields)

        # 1. DBが更新されたか確認
        post.refresh_from_db()
        self.assertEqual(post.title, '新しいタイトル')
        self.assertEqual(post.genre, 'report')
        
        # 2. ベクトル化（再生成）が呼ばれたか確認
        mock_vectorize.assert_called_once_with(post.post_id)

    @patch('ai_features.services.core_services.VectorizationService.vectorize_bbs_comment')
    def test_create_comment(self, mock_vectorize):
        """コメント作成のテスト（コメント数更新も確認）"""
        mock_vectorize.return_value = True

        # 親投稿を作成
        post = BBSPost.objects.create(
            store=self.store,
            user=self.user,
            title="親投稿",
            content="...",
            comment_count=0
        )

        content = "コメントテスト"

        # サービスの実行
        comment = BBSService.create_comment(
            post=post,
            user=self.user,
            content=content
        )

        # 1. コメントがDBに保存されたか
        self.assertEqual(BBSComment.objects.count(), 1)
        
        # 2. 親投稿のコメント数が更新されたか（BBSServiceのロジック）
        post.refresh_from_db()
        self.assertEqual(post.comment_count, 1)

        # 3. ベクトル化が呼ばれたか
        mock_vectorize.assert_called_once_with(comment.comment_id)

    @patch('ai_features.services.core_services.VectorizationService.vectorize_bbs_post')
    def test_create_post_vectorization_failure(self, mock_vectorize):
        """ベクトル化が失敗しても、投稿自体は成功することを確認"""
        # ベクトル化でエラーが発生するように設定
        mock_vectorize.side_effect = Exception("AI Service Down")

        # サービス実行（エラーは内部でキャッチされるはず）
        post = BBSService.create_post(
            store=self.store,
            user=self.user,
            title="エラー耐性テスト",
            content="内容は保存されるべき",
            genre="other"
        )

        # DBには保存されているはず
        self.assertEqual(BBSPost.objects.count(), 1)
        self.assertEqual(post.title, "エラー耐性テスト")
        
        # モックは呼ばれている
        mock_vectorize.assert_called_once()

    @patch('ai_features.services.core_services.VectorizationService.vectorize_bbs_comment')
    def test_update_comment(self, mock_vectorize):
        """コメント更新のテスト"""
        mock_vectorize.return_value = True

        # 投稿とコメントを作成
        post = BBSPost.objects.create(
            store=self.store,
            user=self.user,
            title="投稿",
            content="内容",
            genre="claim"
        )

        comment = BBSComment.objects.create(
            post=post,
            user=self.user,
            content="古いコメント"
        )

        # 更新内容
        update_fields = {
            'content': '新しいコメント',
            'is_best_answer': True
        }

        # サービスの実行
        updated_comment = BBSService.update_comment(comment, update_fields)

        # 1. DBが更新されたか確認
        comment.refresh_from_db()
        self.assertEqual(comment.content, '新しいコメント')
        self.assertTrue(comment.is_best_answer)

        # 2. ベクトル化（再生成）が呼ばれたか確認
        mock_vectorize.assert_called_once_with(comment.comment_id)

    @patch('ai_features.services.core_services.VectorizationService.vectorize_bbs_post')
    def test_revectorize_post_success(self, mock_vectorize):
        """投稿の再ベクトル化が成功することを確認"""
        mock_vectorize.return_value = True

        post = BBSPost.objects.create(
            store=self.store,
            user=self.user,
            title="投稿",
            content="内容",
            genre="claim"
        )

        result = BBSService.revectorize_post(post.post_id)

        self.assertTrue(result)
        mock_vectorize.assert_called_once_with(post.post_id)

    @patch('ai_features.services.core_services.VectorizationService.vectorize_bbs_post')
    def test_revectorize_post_failure(self, mock_vectorize):
        """投稿の再ベクトル化が失敗した場合Falseを返すことを確認"""
        mock_vectorize.return_value = False

        post = BBSPost.objects.create(
            store=self.store,
            user=self.user,
            title="投稿",
            content="内容",
            genre="claim"
        )

        result = BBSService.revectorize_post(post.post_id)

        self.assertFalse(result)

    @patch('ai_features.services.core_services.VectorizationService.vectorize_bbs_post')
    def test_revectorize_post_exception(self, mock_vectorize):
        """投稿の再ベクトル化でエラーが発生した場合Falseを返すことを確認"""
        mock_vectorize.side_effect = Exception("Vectorization error")

        post = BBSPost.objects.create(
            store=self.store,
            user=self.user,
            title="投稿",
            content="内容",
            genre="claim"
        )

        result = BBSService.revectorize_post(post.post_id)

        self.assertFalse(result)

    @patch('ai_features.services.core_services.VectorizationService.vectorize_bbs_comment')
    def test_revectorize_comment_success(self, mock_vectorize):
        """コメントの再ベクトル化が成功することを確認"""
        mock_vectorize.return_value = True

        post = BBSPost.objects.create(
            store=self.store,
            user=self.user,
            title="投稿",
            content="内容",
            genre="claim"
        )

        comment = BBSComment.objects.create(
            post=post,
            user=self.user,
            content="コメント"
        )

        result = BBSService.revectorize_comment(comment.comment_id)

        self.assertTrue(result)
        mock_vectorize.assert_called_once_with(comment.comment_id)

    @patch('ai_features.services.core_services.VectorizationService.vectorize_bbs_comment')
    def test_revectorize_comment_failure(self, mock_vectorize):
        """コメントの再ベクトル化が失敗した場合Falseを返すことを確認"""
        mock_vectorize.return_value = False

        post = BBSPost.objects.create(
            store=self.store,
            user=self.user,
            title="投稿",
            content="内容",
            genre="claim"
        )

        comment = BBSComment.objects.create(
            post=post,
            user=self.user,
            content="コメント"
        )

        result = BBSService.revectorize_comment(comment.comment_id)

        self.assertFalse(result)

    @patch('ai_features.services.core_services.VectorizationService.vectorize_bbs_comment')
    def test_revectorize_comment_exception(self, mock_vectorize):
        """コメントの再ベクトル化でエラーが発生した場合Falseを返すことを確認"""
        mock_vectorize.side_effect = Exception("Vectorization error")

        post = BBSPost.objects.create(
            store=self.store,
            user=self.user,
            title="投稿",
            content="内容",
            genre="claim"
        )

        comment = BBSComment.objects.create(
            post=post,
            user=self.user,
            content="コメント"
        )

        result = BBSService.revectorize_comment(comment.comment_id)

        self.assertFalse(result)

    @patch('ai_features.services.core_services.VectorizationService.vectorize_bbs_post')
    def test_update_post_vectorization_failure(self, mock_vectorize):
        """ベクトル化が失敗しても、投稿更新自体は成功することを確認"""
        # 最初の作成時はFalseを返す（更新時もFalseを返すように）
        mock_vectorize.return_value = False

        post = BBSPost.objects.create(
            store=self.store,
            user=self.user,
            title="元のタイトル",
            content="元の内容",
            genre="claim"
        )

        # ベクトル化失敗をシミュレート
        mock_vectorize.side_effect = Exception("AI Service Down")

        update_fields = {'title': '更新されたタイトル'}
        updated_post = BBSService.update_post(post, update_fields)

        # 投稿は更新されている
        post.refresh_from_db()
        self.assertEqual(post.title, '更新されたタイトル')

    @patch('ai_features.services.core_services.VectorizationService.vectorize_bbs_comment')
    def test_create_comment_vectorization_failure(self, mock_vectorize):
        """ベクトル化が失敗しても、コメント作成自体は成功することを確認"""
        mock_vectorize.side_effect = Exception("AI Service Down")

        post = BBSPost.objects.create(
            store=self.store,
            user=self.user,
            title="投稿",
            content="内容",
            comment_count=0
        )

        comment = BBSService.create_comment(
            post=post,
            user=self.user,
            content="コメント内容"
        )

        # コメントは作成されている
        self.assertEqual(BBSComment.objects.count(), 1)
        self.assertEqual(comment.content, "コメント内容")

        # コメント数も更新されている
        post.refresh_from_db()
        self.assertEqual(post.comment_count, 1)

    @patch('ai_features.services.core_services.VectorizationService.vectorize_bbs_comment')
    def test_update_comment_vectorization_failure(self, mock_vectorize):
        """ベクトル化が失敗しても、コメント更新自体は成功することを確認"""
        post = BBSPost.objects.create(
            store=self.store,
            user=self.user,
            title="投稿",
            content="内容"
        )

        comment = BBSComment.objects.create(
            post=post,
            user=self.user,
            content="元のコメント"
        )

        # ベクトル化失敗をシミュレート
        mock_vectorize.side_effect = Exception("AI Service Down")

        update_fields = {'content': '更新されたコメント'}
        updated_comment = BBSService.update_comment(comment, update_fields)

        # コメントは更新されている
        comment.refresh_from_db()
        self.assertEqual(comment.content, '更新されたコメント')
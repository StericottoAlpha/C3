"""
掲示板関連のビジネスロジック
投稿・コメント作成時にベクトル化も実行
"""
import logging
from typing import Optional, Dict, Any
from django.db import transaction
from .models import BBSPost, BBSComment

logger = logging.getLogger(__name__)


class BBSService:
    """掲示板サービス - 投稿・コメントの作成・更新・ベクトル化を管理"""

    @staticmethod
    @transaction.atomic
    def create_post(
        store,
        user,
        title: str,
        content: str,
        report=None,
        **kwargs
    ) -> BBSPost:
        """
        掲示板投稿を作成し、自動的にベクトル化を実行

        Args:
            store: 店舗オブジェクト
            user: ユーザーオブジェクト
            title: タイトル
            content: 本文
            report: 関連する日報（オプション）
            **kwargs: その他のフィールド

        Returns:
            作成されたBBSPostオブジェクト
        """
        # 投稿を作成
        post = BBSPost.objects.create(
            store=store,
            user=user,
            title=title,
            content=content,
            report=report,
            comment_count=0,
            **kwargs
        )

        # ベクトル化を実行
        try:
            from ai_features.services.core_services import VectorizationService
            result = VectorizationService.vectorize_bbs_post(post.post_id)

            if result:
                logger.info(f"掲示板投稿作成＆ベクトル化成功: post_id={post.post_id}")
            else:
                logger.warning(f"掲示板投稿は作成されたがベクトル化失敗: post_id={post.post_id}")

        except Exception as e:
            logger.error(f"掲示板投稿ベクトル化中にエラー: post_id={post.post_id}, error={e}", exc_info=True)

        return post

    @staticmethod
    @transaction.atomic
    def update_post(
        post: BBSPost,
        update_fields: Dict[str, Any]
    ) -> BBSPost:
        """
        掲示板投稿を更新し、ベクトルを再生成

        Args:
            post: 更新対象のBBSPostオブジェクト
            update_fields: 更新するフィールドの辞書

        Returns:
            更新されたBBSPostオブジェクト
        """
        # フィールドを更新
        for field, value in update_fields.items():
            setattr(post, field, value)
        post.save()

        # ベクトルを再生成
        try:
            from ai_features.services.core_services import VectorizationService
            result = VectorizationService.vectorize_bbs_post(post.post_id)

            if result:
                logger.info(f"掲示板投稿更新＆ベクトル化成功: post_id={post.post_id}")
            else:
                logger.warning(f"掲示板投稿は更新されたがベクトル化失敗: post_id={post.post_id}")

        except Exception as e:
            logger.error(f"掲示板投稿ベクトル化中にエラー: post_id={post.post_id}, error={e}", exc_info=True)

        return post

    @staticmethod
    @transaction.atomic
    def create_comment(
        post: BBSPost,
        user,
        content: str,
        is_best_answer: bool = False,
        **kwargs
    ) -> BBSComment:
        """
        掲示板コメントを作成し、自動的にベクトル化を実行

        Args:
            post: 投稿オブジェクト
            user: ユーザーオブジェクト
            content: コメント内容
            is_best_answer: ベストアンサーかどうか
            **kwargs: その他のフィールド

        Returns:
            作成されたBBSCommentオブジェクト
        """
        # コメントを作成
        comment = BBSComment.objects.create(
            post=post,
            user=user,
            content=content,
            is_best_answer=is_best_answer,
            **kwargs
        )

        # 投稿のコメント数を更新
        post.comment_count = post.comments.count()
        post.save()

        # ベクトル化を実行
        try:
            from ai_features.services.core_services import VectorizationService
            result = VectorizationService.vectorize_bbs_comment(comment.comment_id)

            if result:
                logger.info(f"掲示板コメント作成＆ベクトル化成功: comment_id={comment.comment_id}")
            else:
                logger.warning(f"掲示板コメントは作成されたがベクトル化失敗: comment_id={comment.comment_id}")

        except Exception as e:
            logger.error(f"掲示板コメントベクトル化中にエラー: comment_id={comment.comment_id}, error={e}", exc_info=True)

        return comment

    @staticmethod
    @transaction.atomic
    def update_comment(
        comment: BBSComment,
        update_fields: Dict[str, Any]
    ) -> BBSComment:
        """
        掲示板コメントを更新し、ベクトルを再生成

        Args:
            comment: 更新対象のBBSCommentオブジェクト
            update_fields: 更新するフィールドの辞書

        Returns:
            更新されたBBSCommentオブジェクト
        """
        # フィールドを更新
        for field, value in update_fields.items():
            setattr(comment, field, value)
        comment.save()

        # ベクトルを再生成
        try:
            from ai_features.services.core_services import VectorizationService
            result = VectorizationService.vectorize_bbs_comment(comment.comment_id)

            if result:
                logger.info(f"掲示板コメント更新＆ベクトル化成功: comment_id={comment.comment_id}")
            else:
                logger.warning(f"掲示板コメントは更新されたがベクトル化失敗: comment_id={comment.comment_id}")

        except Exception as e:
            logger.error(f"掲示板コメントベクトル化中にエラー: comment_id={comment.comment_id}, error={e}", exc_info=True)

        return comment

    @staticmethod
    def revectorize_post(post_id: int) -> bool:
        """
        既存の掲示板投稿を再ベクトル化（手動実行用）

        Args:
            post_id: 投稿ID

        Returns:
            成功した場合True
        """
        try:
            from ai_features.services.core_services import VectorizationService
            result = VectorizationService.vectorize_bbs_post(post_id)

            if result:
                logger.info(f"掲示板投稿再ベクトル化成功: post_id={post_id}")
            else:
                logger.warning(f"掲示板投稿再ベクトル化失敗: post_id={post_id}")

            return result

        except Exception as e:
            logger.error(f"掲示板投稿再ベクトル化中にエラー: post_id={post_id}, error={e}", exc_info=True)
            return False

    @staticmethod
    def revectorize_comment(comment_id: int) -> bool:
        """
        既存の掲示板コメントを再ベクトル化（手動実行用）

        Args:
            comment_id: コメントID

        Returns:
            成功した場合True
        """
        try:
            from ai_features.services.core_services import VectorizationService
            result = VectorizationService.vectorize_bbs_comment(comment_id)

            if result:
                logger.info(f"掲示板コメント再ベクトル化成功: comment_id={comment_id}")
            else:
                logger.warning(f"掲示板コメント再ベクトル化失敗: comment_id={comment_id}")

            return result

        except Exception as e:
            logger.error(f"掲示板コメント再ベクトル化中にエラー: comment_id={comment_id}, error={e}", exc_info=True)
            return False

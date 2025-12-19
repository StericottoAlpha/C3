"""
日報関連のビジネスロジック
作成・更新時にベクトル化も実行
"""
import logging
from typing import Optional, Dict, Any
from django.db import transaction
from .models import DailyReport

logger = logging.getLogger(__name__)


class DailyReportService:
    """日報サービス - 作成・更新・ベクトル化を管理"""

    @staticmethod
    @transaction.atomic
    def create_report(
        store,
        user,
        date,
        genre: str,
        location: str,
        title: str,
        content: str,
        post_to_bbs: bool = False,
        **kwargs
    ) -> DailyReport:
        """
        日報を作成し、自動的にベクトル化を実行

        Args:
            store: 店舗オブジェクト
            user: ユーザーオブジェクト
            date: 日付
            genre: ジャンル (claim/praise/accident/report/other)
            location: 場所 (kitchen/hall/cashier/toilet/other)
            title: タイトル
            content: 内容
            post_to_bbs: 掲示板に投稿するか
            **kwargs: その他のフィールド

        Returns:
            作成されたDailyReportオブジェクト
        """
        # 日報を作成
        report = DailyReport.objects.create(
            store=store,
            user=user,
            date=date,
            genre=genre,
            location=location,
            title=title,
            content=content,
            post_to_bbs=post_to_bbs,
            **kwargs
        )

        # ベクトル化を実行
        try:
            from ai_features.services.core_services import VectorizationService
            result = VectorizationService.vectorize_daily_report(report.report_id)

            if result:
                logger.info(f"日報作成＆ベクトル化成功: report_id={report.report_id}")
            else:
                logger.warning(f"日報は作成されたがベクトル化失敗: report_id={report.report_id}")

        except Exception as e:
            logger.error(f"日報ベクトル化中にエラー: report_id={report.report_id}, error={e}", exc_info=True)
            # ベクトル化失敗してもトランザクションはロールバックしない（日報自体は保存）

        return report

    @staticmethod
    @transaction.atomic
    def update_report(
        report: DailyReport,
        update_fields: Dict[str, Any]
    ) -> DailyReport:
        """
        日報を更新し、ベクトルを再生成

        Args:
            report: 更新対象のDailyReportオブジェクト
            update_fields: 更新するフィールドの辞書

        Returns:
            更新されたDailyReportオブジェクト
        """
        # フィールドを更新
        for field, value in update_fields.items():
            setattr(report, field, value)
        report.save()

        # ベクトルを再生成
        try:
            from ai_features.services.core_services import VectorizationService
            result = VectorizationService.vectorize_daily_report(report.report_id)

            if result:
                logger.info(f"日報更新＆ベクトル化成功: report_id={report.report_id}")
            else:
                logger.warning(f"日報は更新されたがベクトル化失敗: report_id={report.report_id}")

        except Exception as e:
            logger.error(f"日報ベクトル化中にエラー: report_id={report.report_id}, error={e}", exc_info=True)

        return report

    @staticmethod
    def revectorize_report(report_id: int) -> bool:
        """
        既存の日報を再ベクトル化（手動実行用）

        Args:
            report_id: 日報ID

        Returns:
            成功した場合True
        """
        try:
            from ai_features.services.core_services import VectorizationService
            result = VectorizationService.vectorize_daily_report(report_id)

            if result:
                logger.info(f"日報再ベクトル化成功: report_id={report_id}")
            else:
                logger.warning(f"日報再ベクトル化失敗: report_id={report_id}")

            return result

        except Exception as e:
            logger.error(f"日報再ベクトル化中にエラー: report_id={report_id}, error={e}", exc_info=True)
            return False

from django.test import TestCase
from stores.models import Store, MonthlyGoal
from reports.models import DailyReport, StoreDailyPerformance

class AnalyticsModelDependencyTests(TestCase):
    """
    analyticsアプリが依存する外部モデルの連携テスト
    """

    def test_dependent_models_exist(self):
        """
        集計対象となるモデルが正常にインポートでき、
        Managerが動作することを確認する
        """
        # 単なる存在確認
        self.assertTrue(hasattr(Store, 'objects'))
        self.assertTrue(hasattr(DailyReport, 'objects'))
        self.assertTrue(hasattr(StoreDailyPerformance, 'objects'))
        self.assertTrue(hasattr(MonthlyGoal, 'objects'))
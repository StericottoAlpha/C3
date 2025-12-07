from django.db import models

# グラフデータはリアルタイムでAPIから生成するため、
# このアプリではモデルを定義しません。
#
# グラフデータは以下から動的に集計されます:
# - reports.models.StoreDailyPerformance (売上、客数)
# - reports.models.DailyReport (インシデント数)
# - bbs.models.BBSPost (掲示板投稿数)

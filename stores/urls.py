from django.urls import path
from . import views

app_name = 'stores'

urlpatterns = [
    # 既存のパスがあれば残し、以下を追加
    path('goal/update/', views.update_current_month_goal, name='update_goal'),
]
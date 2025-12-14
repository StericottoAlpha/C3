from django.urls import path

from . import views

app_name = 'analytics'

urlpatterns = [
    path('', views.dashboard, name='dashboard'),
    path('api/graph-data/', views.get_graph_data, name='graph_data'),
    path('api/monthly-goal/', views.get_monthly_goal, name='monthly_goal'),
]

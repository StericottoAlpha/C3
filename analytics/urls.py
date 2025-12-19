from django.urls import path

from . import views

app_name = 'analytics'

urlpatterns = [
    path('graph/own_store/', views.dashboard, {'default_scope': 'own'}, name='dashboard'),
    path('graph/all_store/', views.dashboard, {'default_scope': 'all'}, name='dashboard_all'),
    path('api/graph-data/', views.get_graph_data, name='graph_data'),
    path('api/monthly-goal/', views.get_monthly_goal, name='monthly_goal'),
]

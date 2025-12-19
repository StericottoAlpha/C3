from django.urls import path

from . import views

app_name = 'analytics'

urlpatterns = [
    path('', views.dashboard, name='dashboard'),
    path("calendar/", views.calendar_view, name="calendar"),
    path("calendar/day/<slug:ymd>/", views.calendar_day_api, name="calendar_day_api"),
    path("calendar/detail/<int:report_id>/", views.calendar_detail, name="calendar_detail"),
    path('graph/own_store/', views.dashboard, name='dashboard'),
    path('api/graph-data/', views.get_graph_data, name='graph_data'),
    path('api/monthly-goal/', views.get_monthly_goal, name='monthly_goal'),
]

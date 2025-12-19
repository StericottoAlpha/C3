from django.urls import path

from . import views

app_name = 'analytics'

urlpatterns = [
    path('', views.dashboard, name='dashboard'),
    path("calendar/", views.calendar_view, name="calendar"),
    path("calendar/day/<slug:ymd>/", views.calendar_day_api, name="calendar_day_api"),
    path("calendar/detail/<int:report_id>/", views.calendar_detail, name="calendar_detail"),
]

from django.urls import path

from . import views

app_name = 'reports'

urlpatterns = [
    path('view/<int:report_id>/', views.report_view, name='view'),
    # path('', views.report_list, name='list'),
    # path('create/', views.report_create, name='create'),
]

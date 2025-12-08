from django.urls import path

from . import views

app_name = 'reports'

urlpatterns = [
    path('register/', views.report_register, name='register'),
    # path('', views.report_list, name='list'),
    # path('<int:pk>/', views.report_detail, name='detail'),
]

from django.urls import path

from . import views

app_name = 'reports'

urlpatterns = [
    path('register/', views.report_register, name='register'),
    path('view/<int:report_id>/', views.report_view, name='view'),
]

from django.urls import path

from . import views

app_name = 'bbs'

urlpatterns = [
    path('list/', views.bbs_list, name='list'),
    path('register/', views.bbs_register, name='register'),
]

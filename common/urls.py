from django.urls import path
from . import views

app_name = 'common'

urlpatterns = [
    path('', views.index, name='index'),
    path('health/', views.health, name="health"),
    # path('debug/storage/', views.debug_storage, name='debug_storage'),  # 一時的なデバッグ用

    # PWA
    path('manifest.json', views.manifest, name='manifest'),
    path('service-worker.js', views.service_worker, name='service_worker'),
]

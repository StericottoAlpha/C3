from django.urls import path
from . import views

app_name = 'common'

urlpatterns = [
    path('', views.index, name='index'),
    path('health/', views.health, name="health"),

    # PWA
    path('manifest.json', views.manifest, name='manifest'),
    path('service-worker.js', views.service_worker, name='service_worker'),
]

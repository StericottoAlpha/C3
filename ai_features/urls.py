from django.urls import path

from . import views

app_name = 'ai_features'

urlpatterns = [
    # Chat endpoints
    path('api/chat/', views.ChatView.as_view(), name='chat'),
    path('api/chat/history/', views.chat_history_view, name='chat_history'),
    path('api/chat/history/clear/', views.clear_chat_history_view, name='clear_chat_history'),

    # Status endpoint
    path('api/status/', views.agent_status_view, name='agent_status'),
]

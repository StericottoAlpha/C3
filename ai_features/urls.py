from django.urls import path

from . import views

app_name = 'ai_features'

urlpatterns = [

    path('ai/chat/', views.chat_page_view, name="chat_page"),
    # Chat endpoints
    path('api/chat/', views.ChatView.as_view(), name='chat'),
    #path('api/chat/stream/', views.chat_stream_view, name='chat_stream'),  # ストリーミング対応
    #path('api/chat/parallel/', views.ChatParallelView.as_view(), name='chat_parallel'),  # 並列ツール実行
    path('api/chat/history/', views.chat_history_view, name='chat_history'),
    path('api/chat/history/clear/', views.clear_chat_history_view, name='clear_chat_history'),

    # Status endpoint
    #path('api/status/', views.agent_status_view, name='agent_status'),
]
from django.urls import path

from . import views

app_name = 'accounts'

urlpatterns = [
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('profile/', views.profile_view, name='profile'),  
    path('signup/', views.signup_view, name='signup'),
    path('staff-list/', views.staff_list_view, name='staff_list'),
    path('staff-edit/<str:user_id>/', views.staff_edit_view, name='staff_edit'),
]
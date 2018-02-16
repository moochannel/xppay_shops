from django.contrib.auth import views as auth_views
from django.urls import path

from .views import UserDetail, index

app_name = 'accounts'
urlpatterns = [
    path('', index, name='index'),
    path('login', auth_views.login, {'template_name': 'accounts/login.html'}, name='login'),
    path('logout', auth_views.logout, name='logout'),
    path('profile', UserDetail.as_view(), name='profile_edit'),
]

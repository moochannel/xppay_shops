from django.urls import path

from . import views

app_name = 'payments'
urlpatterns = [
    path('rate/', views.xp2jpy_rate, name='xpjpy_rate'),
    path('about_xppay/', views.AboutPayView.as_view(), name='about_xppay'),
    path('about_site/', views.AboutSiteView.as_view(), name='about_site'),
    path('howto_register/', views.HowtoRegisterView.as_view(), name='howto_register'),
]

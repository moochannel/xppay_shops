from django.urls import path

from .views import ShopList

urlpatterns = [
    path('', ShopList.as_view(), name='index'),
]

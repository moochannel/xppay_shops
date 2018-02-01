from django.urls import path

from .views import ShopList, ShopDetail

urlpatterns = [
    path('', ShopList.as_view(), name='index'),
    path('<int:pk>/', ShopDetail.as_view(), name='shop_detail')
]

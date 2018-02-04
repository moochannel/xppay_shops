from django.urls import path

from .views import ShopList, ShopDetail, ShopCreate, ShopUpdate

urlpatterns = [
    path('', ShopList.as_view(), name='index'),
    path('<int:pk>/', ShopDetail.as_view(), name='shop_detail'),
    path('add/', ShopCreate.as_view(), name='shop_add'),
    path('<int:pk>/edit/', ShopUpdate.as_view(), name='shop_edit'),
]

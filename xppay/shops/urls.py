from django.urls import path

from .views import (
    BenefitCreate, BenefitList, BenefitUpdate, PhotoCreate, PhotoDelete, PhotoList, ShopCreate,
    ShopDetail, ShopList, ShopUpdate
)

app_name = 'shops'
urlpatterns = [
    path('', ShopList.as_view(), name='shop_list'),
    path('<slug>/', ShopDetail.as_view(), name='shop_detail'),
    path('add/', ShopCreate.as_view(), name='shop_add'),
    path('<slug>/edit/', ShopUpdate.as_view(), name='shop_edit'),
    path('<slug>/benefits/', BenefitList.as_view(), name='benefit_list'),
    path('<slug>/benefits/add/', BenefitCreate.as_view(), name='benefit_add'),
    path(
        '<slug>/benefits/<int:pk>/edit/', BenefitUpdate.as_view(), name='benefit_edit'
    ),
    path('<slug>/photos/', PhotoList.as_view(), name='photo_list'),
    path('<slug>/photos/add/', PhotoCreate.as_view(), name='photo_add'),
    path('<slug>/photos/<int:pk>/del/', PhotoDelete.as_view(), name='photo_del'),
]

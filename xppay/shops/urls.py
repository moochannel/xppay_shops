from django.urls import path

from .views import (
    BenefitCreate, BenefitList, BenefitUpdate, PhotoCreate, PhotoDelete, PhotoList, ShopCreate,
    ShopDetail, ShopList, ShopUpdate
)

app_name = 'shops'
urlpatterns = [
    path('', ShopList.as_view(), name='shop_list'),
    path('<int:pk>/', ShopDetail.as_view(), name='shop_detail'),
    path('add/', ShopCreate.as_view(), name='shop_add'),
    path('<int:pk>/edit/', ShopUpdate.as_view(), name='shop_edit'),
    path('<int:shop_id>/benefits/', BenefitList.as_view(), name='benefit_list'),
    path('<int:shop_id>/benefits/add/', BenefitCreate.as_view(), name='benefit_add'),
    path(
        '<int:shop_id>/benefits/<int:pk>/edit/', BenefitUpdate.as_view(), name='benefit_edit'
    ),
    path('<int:shop_id>/photos/', PhotoList.as_view(), name='photo_list'),
    path('<int:shop_id>/photos/add/', PhotoCreate.as_view(), name='photo_add'),
    path('<int:shop_id>/photos/<int:pk>/del/', PhotoDelete.as_view(), name='photo_del'),
]

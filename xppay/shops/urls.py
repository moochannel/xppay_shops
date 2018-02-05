from django.urls import path

from .views import (
    BenefitCreate, BenefitList, BenefitUpdate, ShopCreate, ShopDetail, ShopList, ShopUpdate
)

urlpatterns = [
    path('', ShopList.as_view(), name='index'),
    path('<int:pk>/', ShopDetail.as_view(), name='shop_detail'),
    path('add/', ShopCreate.as_view(), name='shop_add'),
    path('<int:pk>/edit/', ShopUpdate.as_view(), name='shop_edit'),
    path('<int:shop_id>/benefits/', BenefitList.as_view(), name='shop_benefit_list'),
    path('<int:shop_id>/benefits/add/', BenefitCreate.as_view(), name='shop_benefit_add'),
    path(
        '<int:shop_id>/benefits/<int:pk>/edit/', BenefitUpdate.as_view(), name='shop_benefit_edit'
    ),
]

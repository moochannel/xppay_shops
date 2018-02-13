from django.urls import path

from .views import (
    BenefitCreate, BenefitList, BenefitUpdate, ContactCreate, ContactDelete, ContactList,
    ContactUpdate, PhotoCreate, PhotoDelete, PhotoList, ShopApprovalCancel, ShopApprovalCreate,
    ShopApprovalHistory, ShopCreate, ShopDetail, ShopList, ShopPdf, ShopUpdate
)

app_name = 'shops'
urlpatterns = [
    path('', ShopList.as_view(), name='shop_list'),
    path('add/', ShopCreate.as_view(), name='shop_add'),
    path('<slug>/', ShopDetail.as_view(), name='shop_detail'),
    path('<slug>/pdf/', ShopPdf.as_view(), name='shop_pdf'),
    path('<slug>/edit/', ShopUpdate.as_view(), name='shop_edit'),
    path('<slug>/contacts/', ContactList.as_view(), name='contact_list'),
    path('<slug>/contacts/add/', ContactCreate.as_view(), name='contact_add'),
    path('<slug>/contacts/<int:pk>/edit/', ContactUpdate.as_view(), name='contact_edit'),
    path('<slug>/contacts/<int:pk>/del/', ContactDelete.as_view(), name='contact_del'),
    path('<slug>/benefits/', BenefitList.as_view(), name='benefit_list'),
    path('<slug>/benefits/add/', BenefitCreate.as_view(), name='benefit_add'),
    path('<slug>/benefits/<int:pk>/edit/', BenefitUpdate.as_view(), name='benefit_edit'),
    path('<slug>/photos/', PhotoList.as_view(), name='photo_list'),
    path('<slug>/photos/add/', PhotoCreate.as_view(), name='photo_add'),
    path('<slug>/photos/<int:pk>/del/', PhotoDelete.as_view(), name='photo_del'),
    path('<slug>/approvals/', ShopApprovalHistory.as_view(), name='approve_list'),
    path('<slug>/approvals/add/', ShopApprovalCreate.as_view(), name='approve_add'),
    path('<slug>/approvals/<int:pk>/cacnel/', ShopApprovalCancel.as_view(), name='approve_cancel'),
]

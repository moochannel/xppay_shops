from django.urls import path

from .views import (
    BenefitCancel, BenefitCreate, BenefitDelete, BenefitList, BenefitUpdate, ContactCreate,
    ContactDelete, ContactList, ContactUpdate, PhotoCreate, PhotoDelete, PhotoList,
    ShopApprovalCancel, ShopApprovalCreate, ShopApprovalHistory, ShopApprovalUpdate,
    ShopApprovalWaitingList, ShopCreate, ShopDetail, ShopList, ShopPdf, ShopUpdate, StaffDelete,
    StaffList
)

app_name = 'shops'
urlpatterns = [
    path('', ShopList.as_view(), name='shop_list'),
    path('all/', ShopList.as_view(), name='shop_list_all', kwargs={
        'all_shop': True
    }),
    path('add/', ShopCreate.as_view(), name='shop_add'),
    path('waiting/', ShopApprovalWaitingList.as_view(), name='approve_waiting'),
    path('waiting/<int:pk>/', ShopApprovalUpdate.as_view(), name='approve_update'),
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
    path('<slug>/benefits/<int:pk>/cancel/', BenefitCancel.as_view(), name='benefit_cancel'),
    path('<slug>/benefits/<int:pk>/del/', BenefitDelete.as_view(), name='benefit_del'),
    path('<slug>/photos/', PhotoList.as_view(), name='photo_list'),
    path('<slug>/photos/add/', PhotoCreate.as_view(), name='photo_add'),
    path('<slug>/photos/<int:pk>/del/', PhotoDelete.as_view(), name='photo_del'),
    path('<slug>/staffs/', StaffList.as_view(), name='staff_list'),
    path('<slug>/staffs/<int:pk>/del/', StaffDelete.as_view(), name='staff_del'),
    path('<slug>/approvals/', ShopApprovalHistory.as_view(), name='approve_list'),
    path('<slug>/approvals/add/', ShopApprovalCreate.as_view(), name='approve_add'),
    path('<slug>/approvals/<int:pk>/cancel/', ShopApprovalCancel.as_view(), name='approve_cancel'),
]

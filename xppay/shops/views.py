from django.contrib import messages
from django.contrib.auth.mixins import (
    LoginRequiredMixin, PermissionRequiredMixin, UserPassesTestMixin
)
from django.db import IntegrityError, models
from django.shortcuts import get_object_or_404
from django.urls import reverse, reverse_lazy
from django.utils import timezone
from django.views.generic import DetailView, ListView
from django.views.generic.edit import CreateView, DeleteView, UpdateView
from django_weasyprint import WeasyTemplateResponseMixin

from notifications.utils import spam_notify

from .forms import (
    BenefitCancelForm, BenefitForm, ContactForm, PhotoForm, ShopApproveForm,
    ShopApproveRequestForm, ShopForm, StaffForm
)
from .models import (
    Area, Benefit, Contact, Employment, Photo, Shop, ShopApproval, StaffInvitation
)
from .utils import make_qrcode_for_pdf


class ShopList(ListView):
    model = Shop

    def get_queryset(self):
        shop_manager = Shop.objects if 'all_shop' in self.kwargs else Shop.active_objects
        return shop_manager.select_related('area').prefetch_related('photo_set').order_by(
            'area__list_order', 'pk'
        )

    def get_context_data(self, **kwargs):
        shop_manager = Shop.objects if 'all_shop' in self.kwargs else Shop.active_objects
        context = super().get_context_data(**kwargs)
        context['areas'] = Area.objects.prefetch_related(
            models.Prefetch('shops', queryset=shop_manager.all(), to_attr='active_shops')
        ).order_by('list_order')
        return context


def can_edit_shop(self, shop=None):
    if not shop:
        shop = self.get_object()
    user = self.request.user
    return (
        user.has_perm('shops.can_approve') or shop.created_by == user or user in shop.staffs.all()
    )


class ShopDetail(DetailView):
    model = Shop

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['can_edit_shop'] = can_edit_shop(self)
        return context


class ShopCreate(LoginRequiredMixin, CreateView):
    model = Shop
    form_class = ShopForm
    raise_exception = True

    def get_initial(self):
        initial = super().get_initial()
        initial['discord_for_payment'] = f'@{self.request.user.discord_name}'
        return initial

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['active_subtab'] = 'shop'
        return context

    def form_valid(self, form):
        form.instance.created_by = self.request.user
        form.instance.updated_by = self.request.user
        response = super().form_valid(form)
        emp = Employment(shop=form.instance, staff=self.request.user)
        emp.save()
        messages.success(self.request, '基本情報を追加しました')
        return response


class ShopUpdate(UserPassesTestMixin, UpdateView):
    model = Shop
    form_class = ShopForm
    raise_exception = True
    test_func = can_edit_shop

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['active_subtab'] = 'shop'
        return context

    def form_valid(self, form):
        form.instance.updated_by = self.request.user
        messages.success(self.request, '基本情報を更新しました')
        return super().form_valid(form)


class ShopPdf(WeasyTemplateResponseMixin, DetailView):
    model = Shop
    template_name = 'shops/shop_pdf.html'


class ShopPaying(DetailView):
    model = Shop
    template_name = 'shops/shop_paying.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['can_edit_shop'] = can_edit_shop(self)
        return context


class ContactList(UserPassesTestMixin, ListView):
    model = Contact
    raise_exception = True

    def test_func(self):
        self.shop = get_object_or_404(Shop, slug=self.kwargs['slug'])
        return can_edit_shop(self, self.shop)

    def get_queryset(self):
        return self.shop.contact_set.order_by('list_order')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['shop'] = self.shop
        context['active_subtab'] = 'contact'
        return context


class ContactCreate(UserPassesTestMixin, CreateView):
    model = Contact
    form_class = ContactForm
    raise_exception = True

    def test_func(self):
        self.shop = get_object_or_404(Shop, slug=self.kwargs['slug'])
        return can_edit_shop(self, self.shop)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['shop'] = self.shop
        context['active_subtab'] = 'contact'
        return context

    def form_valid(self, form):
        shop = get_object_or_404(Shop, slug=self.kwargs['slug'])
        form.instance.shop = shop
        messages.success(self.request, '連絡先を追加しました')
        return super().form_valid(form)


class ContactUpdate(UserPassesTestMixin, UpdateView):
    model = Contact
    form_class = ContactForm
    raise_exception = True

    def test_func(self):
        self.shop = get_object_or_404(Shop, slug=self.kwargs['slug'])
        return can_edit_shop(self, self.shop)

    def get_queryset(self):
        return self.shop.contact_set.all()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['shop'] = get_object_or_404(Shop, slug=self.kwargs['slug'])
        context['active_subtab'] = 'contact'
        return context

    def form_valid(self, form):
        messages.success(self.request, '連絡先を更新しました')
        return super().form_valid(form)


class ContactDelete(UserPassesTestMixin, DeleteView):
    model = Contact
    raise_exception = True

    def test_func(self):
        self.shop = get_object_or_404(Shop, slug=self.kwargs['slug'])
        return can_edit_shop(self, self.shop)

    def get_queryset(self):
        return self.shop.contact_set.all()

    def get_success_url(self):
        return reverse_lazy('shops:contact_list', kwargs={'slug': self.object.shop.slug})

    def delete(self, request, *args, **kwargs):
        messages.success(request, '連絡先を削除しました')
        return super().delete(request, *args, **kwargs)


class BenefitList(UserPassesTestMixin, ListView):
    model = Benefit
    raise_exception = True

    def test_func(self):
        self.shop = get_object_or_404(Shop, slug=self.kwargs['slug'])
        return can_edit_shop(self, self.shop)

    def get_queryset(self):
        basis_dt = timezone.now()
        return self.shop.benefit_set.annotate(
            state=models.Case(
                models.When(ends_at__lt=basis_dt, then=models.Value(-1)),
                models.When(starts_at__gt=basis_dt, then=models.Value(0)),
                default=models.Value(1),
                output_field=models.IntegerField(),
            )
        ).order_by('-state', '-ends_at', '-starts_at')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['shop'] = self.shop
        context['active_subtab'] = 'benefit'
        return context


class BenefitCreate(UserPassesTestMixin, CreateView):
    model = Benefit
    form_class = BenefitForm
    raise_exception = True

    def test_func(self):
        self.shop = get_object_or_404(Shop, slug=self.kwargs['slug'])
        return can_edit_shop(self, self.shop)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['shop'] = self.shop
        context['active_subtab'] = 'benefit'
        return context

    def form_valid(self, form):
        shop = get_object_or_404(Shop, slug=self.kwargs['slug'])
        form.instance.shop = shop
        messages.success(self.request, '特典を追加しました')
        return super().form_valid(form)


class BenefitUpdate(UserPassesTestMixin, UpdateView):
    model = Benefit
    form_class = BenefitForm
    raise_exception = True

    def test_func(self):
        self.shop = get_object_or_404(Shop, slug=self.kwargs['slug'])
        return can_edit_shop(self, self.shop)

    def get_queryset(self):
        return self.shop.benefit_set.all()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['shop'] = self.shop
        context['active_subtab'] = 'benefit'
        return context

    def form_valid(self, form):
        messages.success(self.request, '特典を更新しました')
        return super().form_valid(form)


class BenefitCancel(UserPassesTestMixin, UpdateView):
    model = Benefit
    form_class = BenefitCancelForm
    template_name = 'shops/benefit_cancel_form.html'
    raise_exception = True

    def test_func(self):
        self.shop = get_object_or_404(Shop, slug=self.kwargs['slug'])
        return can_edit_shop(self, self.shop)

    def get_queryset(self):
        return self.shop.benefit_set.all()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['shop'] = self.shop
        context['active_subtab'] = 'benefit'
        return context

    def form_valid(self, form):
        form.instance.ends_at = timezone.now()
        form.instance.updated_by = self.request.user
        messages.success(self.request, '特典を取り下げました')
        return super().form_valid(form)


class BenefitDelete(UserPassesTestMixin, DeleteView):
    model = Benefit
    template_name = 'shops/benefit_delete_form.html'
    raise_exception = True

    def test_func(self):
        self.shop = get_object_or_404(Shop, slug=self.kwargs['slug'])
        return can_edit_shop(self, self.shop)

    def get_queryset(self):
        return self.shop.benefit_set.all()

    def get_success_url(self):
        return reverse_lazy('shops:benefit_list', kwargs={'slug': self.object.shop.slug})

    def delete(self, request, *args, **kwargs):
        messages.success(request, '特典を削除しました')
        return super().delete(request, *args, **kwargs)


class PhotoList(UserPassesTestMixin, CreateView):
    model = Photo
    form_class = PhotoForm
    template_name = 'shops/photo_list.html'
    raise_exception = True

    def test_func(self):
        self.shop = get_object_or_404(Shop, slug=self.kwargs['slug'])
        return can_edit_shop(self, self.shop)

    def get_queryset(self):
        return self.shop.photo_set.all()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['shop'] = self.shop
        context['active_subtab'] = 'photo'
        return context

    def form_valid(self, form):
        shop = get_object_or_404(Shop, slug=self.kwargs['slug'])
        form.instance.shop = shop
        messages.success(self.request, '店舗画像を追加しました')
        return super().form_valid(form)


class PhotoDelete(UserPassesTestMixin, DeleteView):
    model = Photo
    raise_exception = True

    def test_func(self):
        self.shop = get_object_or_404(Shop, slug=self.kwargs['slug'])
        return can_edit_shop(self, self.shop)

    def get_queryset(self):
        return self.shop.photo_set.all()

    def get_success_url(self):
        return reverse_lazy('shops:photo_list', kwargs={'slug': self.object.shop.slug})

    def delete(self, request, *args, **kwargs):
        messages.success(request, '店舗画像を削除しました')
        return super().delete(request, *args, **kwargs)


class ShopApprovalWaitingList(PermissionRequiredMixin, ListView):
    model = ShopApproval
    permission_required = ('shops.can_approve')
    raise_exception = True

    def get_queryset(self):
        return ShopApproval.waiting_objects.order_by('-updated_at')


class ShopApprovalHistory(UserPassesTestMixin, ListView):
    model = ShopApproval
    template_name = 'shops/shopapproval_history.html'
    raise_exception = True

    def test_func(self):
        self.shop = get_object_or_404(Shop, slug=self.kwargs['slug'])
        return can_edit_shop(self, self.shop)

    def get_queryset(self):
        return self.shop.approvals.order_by('-pk')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['shop'] = self.shop
        context['active_subtab'] = 'approval'
        return context


class ShopApprovalCreate(UserPassesTestMixin, CreateView):
    model = ShopApproval
    form_class = ShopApproveRequestForm
    template_name = 'shops/shopapproval_req_form.html'
    raise_exception = True

    def test_func(self):
        self.shop = get_object_or_404(Shop, slug=self.kwargs['slug'])
        return can_edit_shop(self, self.shop)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['shop'] = self.shop
        context['active_subtab'] = 'approval'
        return context

    def form_valid(self, form):
        shop = get_object_or_404(Shop, slug=self.kwargs['slug'])
        form.instance.shop = shop
        form.instance.requested_by = self.request.user
        form.instance.updated_by = self.request.user
        messages.success(self.request, '承認依頼を追加しました')
        response = super().form_valid(form)
        self.notify(form.instance)
        return response

    def notify(self, instance):
        approval_url = self.request.build_absolute_uri(
            reverse('shops:approve_update', kwargs={
                'pk': instance.pk
            })
        )
        payload = f'''承認依頼が登録されました。XPpay SHOPSのサイトで店舗情報をご確認の上、承認してください。
店舗名: {instance.shop.name}
承認依頼URL: {approval_url}
'''

        spam_notify(payload)

    def get_success_url(self):
        return reverse_lazy('shops:approve_list', kwargs={'slug': self.object.shop.slug})


class ShopApprovalUpdate(PermissionRequiredMixin, UpdateView):
    model = ShopApproval
    form_class = ShopApproveForm
    permission_required = ('shops.can_approve')
    raise_exception = True

    def form_valid(self, form):
        form.instance.updated_by = self.request.user
        messages.success(self.request, '承認依頼を更新しました')
        return super().form_valid(form)

    def get_success_url(self):
        return reverse_lazy('shops:approve_waiting')


class ShopApprovalCancel(UserPassesTestMixin, UpdateView):
    model = ShopApproval
    form_class = ShopApproveRequestForm
    template_name = 'shops/shopapproval_cancel_form.html'
    raise_exception = True

    def test_func(self):
        self.shop = get_object_or_404(Shop, slug=self.kwargs['slug'])
        return can_edit_shop(self, self.shop)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['shop'] = self.shop
        context['active_subtab'] = 'approval'
        return context

    def form_valid(self, form):
        form.instance.canceled_at = timezone.now()
        form.instance.canceled_by = form.instance.updated_by = self.request.user
        messages.success(self.request, '承認依頼を取り下げました')
        return super().form_valid(form)

    def get_success_url(self):
        return reverse_lazy('shops:approve_list', kwargs={'slug': self.object.shop.slug})


class StaffList(UserPassesTestMixin, CreateView):
    model = Employment
    form_class = StaffForm
    template_name = 'shops/staff_list.html'
    raise_exception = True

    def test_func(self):
        self.shop = get_object_or_404(Shop, slug=self.kwargs['slug'])
        return can_edit_shop(self, self.shop)

    def get_queryset(self):
        return self.shop.staffs.order_by('pk')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['shop'] = self.shop
        context['active_subtab'] = 'staff'
        return context

    def form_valid(self, form):
        form.instance.shop = self.shop
        form.instance.invited_by = self.request.user
        form.instance.invited_at = timezone.now()
        try:
            result = super().form_valid(form)
            messages.success(self.request, 'スタッフを追加しました')
            return result
        except IntegrityError as err:
            form.add_error('staff', '既に追加されています')
            return super().form_invalid(form)

    def get_success_url(self):
        return reverse_lazy('shops:staff_list', kwargs={'slug': self.shop.slug})


class StaffDelete(UserPassesTestMixin, DeleteView):
    model = Employment
    form_class = StaffForm
    template_name = 'shops/staff_remove_form.html'
    raise_exception = True

    def test_func(self):
        self.shop = get_object_or_404(Shop, slug=self.kwargs['slug'])
        return can_edit_shop(self, self.shop)

    def get_queryset(self):
        return self.shop.employment_set.all()

    def get_success_url(self):
        return reverse_lazy('shops:staff_list', kwargs={'slug': self.shop.slug})

    def delete(self, request, *args, **kwargs):
        messages.success(request, 'スタッフ登録を解除しました')
        return super().delete(request, *args, **kwargs)


class StaffInvite(UserPassesTestMixin, DetailView):
    model = Shop
    template_name = 'shops/staff_invite.html'
    raise_exception = True

    def test_func(self):
        self.shop = get_object_or_404(Shop, slug=self.kwargs['slug'])
        return can_edit_shop(self, self.shop)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        invitation = self.object.staff_invitations.create(invited_by=self.request.user)
        invitation.save()

        invitation_url = self.request.build_absolute_uri(
            reverse(
                'shops:staff_accept',
                kwargs={
                    'slug': invitation.shop.slug,
                    'token': invitation.token
                }
            )
        )
        context['invitation_url'] = invitation_url
        context['invitation_qr_bin'] = make_qrcode_for_pdf(invitation_url, 5)
        return context


class StaffAccept(DetailView):
    model = StaffInvitation
    template_name = 'shops/staff_accepted.html'

    def get_object(self, queryset=None):
        self.shop = get_object_or_404(Shop, slug=self.kwargs['slug'])
        self.invitation = get_object_or_404(StaffInvitation, token=self.kwargs['token'])
        self.error_message = None
        if (self.invitation.accepted_by is not None or self.invitation.accepted_at is not None):
            self.error_message = 'このトークンは使用済みです'
        elif self.invitation.expired_at < timezone.now():
            self.error_message = 'このトークンは使用期限が切れています'
        elif self.invitation.shop != self.shop:
            self.error_message = f'このトークンは{self.shop.name}のものではありません'
        elif self.request.user.is_authenticated:
            if self.request.user in self.shop.staffs.all():
                self.error_message = '既にスタッフとして登録されています'
            else:
                self.invitation.accept(self.request.user)
                messages.success(self.request, 'スタッフを追加しました')

        return self.invitation

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['error_message'] = self.error_message
        return context

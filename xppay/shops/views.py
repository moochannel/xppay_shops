from django.contrib.auth.mixins import (
    LoginRequiredMixin, PermissionRequiredMixin, UserPassesTestMixin
)
from django.db import models
from django.shortcuts import get_object_or_404
from django.urls import reverse_lazy
from django.utils import timezone
from django.views.generic import DetailView, ListView
from django.views.generic.edit import CreateView, DeleteView, UpdateView
from django_weasyprint import WeasyTemplateResponseMixin

from .forms import (
    BenefitForm, ContactForm, PhotoForm, ShopApproveForm, ShopApproveRequestForm, ShopForm
)
from .models import (Area, Benefit, Contact, Employment, Photo, Shop, ShopApproval)


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
        initial['discord_for_payment'] = f'@{self.request.user.username}'
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
        return super().form_valid(form)


class ShopPdf(WeasyTemplateResponseMixin, DetailView):
    model = Shop
    template_name = 'shops/shop_pdf.html'


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


class PhotoList(UserPassesTestMixin, ListView):
    model = Photo
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


class PhotoCreate(UserPassesTestMixin, CreateView):
    model = Photo
    form_class = PhotoForm
    raise_exception = True

    def test_func(self):
        self.shop = get_object_or_404(Shop, slug=self.kwargs['slug'])
        return can_edit_shop(self, self.shop)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['shop'] = self.shop
        context['active_subtab'] = 'photo'
        return context

    def form_valid(self, form):
        shop = get_object_or_404(Shop, slug=self.kwargs['slug'])
        form.instance.shop = shop
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
        return super().form_valid(form)

    def get_success_url(self):
        return reverse_lazy('shops:approve_list', kwargs={'slug': self.object.shop.slug})


class ShopApprovalUpdate(PermissionRequiredMixin, UpdateView):
    model = ShopApproval
    form_class = ShopApproveForm
    permission_required = ('shops.can_approve')
    raise_exception = True

    def form_valid(self, form):
        form.instance.updated_by = self.request.user
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
        return super().form_valid(form)

    def get_success_url(self):
        return reverse_lazy('shops:approve_list', kwargs={'slug': self.object.shop.slug})

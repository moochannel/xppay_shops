from django.contrib.auth.mixins import LoginRequiredMixin
from django.db import models
from django.shortcuts import get_object_or_404
from django.urls import reverse_lazy
from django.utils import timezone
from django.views.generic import DetailView, ListView
from django.views.generic.edit import CreateView, DeleteView, UpdateView
from django_weasyprint import WeasyTemplateResponseMixin

from .forms import (BenefitForm, ContactForm, PhotoForm, ShopApproveRequestForm, ShopForm)
from .models import Area, Benefit, Contact, Photo, Shop, ShopApproval


class ShopList(ListView):
    model = Shop

    def get_queryset(self):
        return Shop.objects.select_related('area').order_by('area__list_order', 'pk')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['areas'] = Area.objects.annotate(
            num_shops=models.Count('shops')
        ).order_by('list_order')
        return context


class ShopDetail(DetailView):
    model = Shop


class ShopCreate(LoginRequiredMixin, CreateView):
    raise_exception = True
    model = Shop
    form_class = ShopForm

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['active_subtab'] = 'shop'
        return context

    def form_valid(self, form):
        form.instance.created_by = self.request.user
        form.instance.updated_by = self.request.user
        return super().form_valid(form)


class ShopUpdate(LoginRequiredMixin, UpdateView):
    raise_exception = True
    model = Shop
    form_class = ShopForm

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


class ContactList(LoginRequiredMixin, ListView):
    raise_exception = True
    model = Contact

    def get_queryset(self):
        self.shop = get_object_or_404(Shop, slug=self.kwargs['slug'])
        return self.shop.contact_set.order_by('list_order')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['shop'] = self.shop
        context['active_subtab'] = 'contact'
        return context


class ContactCreate(LoginRequiredMixin, CreateView):
    raise_exception = True
    model = Contact
    form_class = ContactForm

    def form_valid(self, form):
        shop = get_object_or_404(Shop, slug=self.kwargs['slug'])
        form.instance.shop = shop
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['shop'] = get_object_or_404(Shop, slug=self.kwargs['slug'])
        context['active_subtab'] = 'contact'
        return context


class ContactUpdate(LoginRequiredMixin, UpdateView):
    raise_exception = True
    model = Contact
    form_class = ContactForm

    def get_queryset(self):
        self.shop = get_object_or_404(Shop, slug=self.kwargs['slug'])
        return self.shop.contact_set.all()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['shop'] = get_object_or_404(Shop, slug=self.kwargs['slug'])
        context['active_subtab'] = 'contact'
        return context


class ContactDelete(LoginRequiredMixin, DeleteView):
    raise_exception = True
    model = Contact

    def get_queryset(self):
        self.shop = get_object_or_404(Shop, slug=self.kwargs['slug'])
        return self.shop.contact_set.all()

    def get_success_url(self):
        return reverse_lazy('shops:contact_list', kwargs={'slug': self.object.shop.slug})


class BenefitList(LoginRequiredMixin, ListView):
    raise_exception = True
    model = Benefit

    def get_queryset(self):
        self.shop = get_object_or_404(Shop, slug=self.kwargs['slug'])
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


class BenefitCreate(LoginRequiredMixin, CreateView):
    raise_exception = True
    model = Benefit
    form_class = BenefitForm

    def form_valid(self, form):
        shop = get_object_or_404(Shop, slug=self.kwargs['slug'])
        form.instance.shop = shop
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['shop'] = get_object_or_404(Shop, slug=self.kwargs['slug'])
        context['active_subtab'] = 'benefit'
        return context


class BenefitUpdate(LoginRequiredMixin, UpdateView):
    raise_exception = True
    model = Benefit
    form_class = BenefitForm

    def get_queryset(self):
        self.shop = get_object_or_404(Shop, slug=self.kwargs['slug'])
        return self.shop.benefit_set.all()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['shop'] = get_object_or_404(Shop, slug=self.kwargs['slug'])
        context['active_subtab'] = 'benefit'
        return context


class PhotoList(LoginRequiredMixin, ListView):
    raise_exception = True
    model = Photo

    def get_queryset(self):
        self.shop = get_object_or_404(Shop, slug=self.kwargs['slug'])
        return self.shop.photo_set.all()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['shop'] = self.shop
        context['active_subtab'] = 'photo'
        return context


class PhotoCreate(LoginRequiredMixin, CreateView):
    raise_exception = True
    model = Photo
    form_class = PhotoForm

    def form_valid(self, form):
        shop = get_object_or_404(Shop, slug=self.kwargs['slug'])
        form.instance.shop = shop
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['shop'] = get_object_or_404(Shop, slug=self.kwargs['slug'])
        context['active_subtab'] = 'photo'
        return context


class PhotoDelete(LoginRequiredMixin, DeleteView):
    raise_exception = True
    model = Photo

    def get_queryset(self):
        self.shop = get_object_or_404(Shop, slug=self.kwargs['slug'])
        return self.shop.photo_set.all()

    def get_success_url(self):
        return reverse_lazy('shops:photo_list', kwargs={'slug': self.object.shop.slug})


class ShopApprovalHistory(LoginRequiredMixin, ListView):
    model = ShopApproval

    def get_queryset(self):
        self.shop = get_object_or_404(Shop, slug=self.kwargs['slug'])
        return self.shop.approvals.order_by('-pk')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['shop'] = self.shop
        context['active_subtab'] = 'approval'
        return context


class ShopApprovalCreate(LoginRequiredMixin, CreateView):
    raise_exception = True
    model = ShopApproval
    form_class = ShopApproveRequestForm
    template_name = 'shops/shopapproval_req_form.html'

    def form_valid(self, form):
        shop = get_object_or_404(Shop, slug=self.kwargs['slug'])
        form.instance.shop = shop
        form.instance.requested_by = self.request.user
        form.instance.updated_by = self.request.user
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['shop'] = get_object_or_404(Shop, slug=self.kwargs['slug'])
        context['active_subtab'] = 'approval'
        return context

    def get_success_url(self):
        return reverse_lazy('shops:approve_list', kwargs={'slug': self.object.shop.slug})


class ShopApprovalCancel(LoginRequiredMixin, UpdateView):
    raise_exception = True
    model = ShopApproval
    form_class = ShopApproveRequestForm
    template_name = 'shops/shopapproval_cancel_form.html'

    def form_valid(self, form):
        form.instance.canceled_at = timezone.now()
        form.instance.canceled_by = form.instance.updated_by = self.request.user
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['shop'] = get_object_or_404(Shop, slug=self.kwargs['slug'])
        context['active_subtab'] = 'approval'
        return context

    def get_success_url(self):
        return reverse_lazy('shops:approve_list', kwargs={'slug': self.object.shop.slug})

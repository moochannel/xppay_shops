from django.contrib.auth.mixins import LoginRequiredMixin
from django.db import models
from django.shortcuts import get_object_or_404
from django.urls import reverse_lazy
from django.utils import timezone
from django.views.generic import DetailView, ListView
from django.views.generic.edit import CreateView, DeleteView, UpdateView
from django_weasyprint import WeasyTemplateResponseMixin

from .forms import BenefitForm, PhotoForm, ShopForm
from .models import Area, Benefit, Photo, Shop


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


class ShopUpdate(LoginRequiredMixin, UpdateView):
    raise_exception = True
    model = Shop
    form_class = ShopForm

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['active_subtab'] = 'shop'
        return context


class ShopPdf(WeasyTemplateResponseMixin, DetailView):
    model = Shop
    template_name = 'shops/shop_pdf.html'


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

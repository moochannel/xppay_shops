from django.db.models import Count
from django.views.generic import DetailView, ListView
from django.views.generic.edit import CreateView, UpdateView

from .forms import ShopForm
from .models import Area, Shop


class ShopList(ListView):
    model = Shop

    def get_queryset(self):
        return Shop.objects.select_related('area').order_by('area__list_order', 'pk')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['areas'] = Area.objects.annotate(num_shops=Count('shops')).order_by('list_order')
        return context


class ShopDetail(DetailView):
    model = Shop


class ShopCreate(CreateView):
    model = Shop
    form_class = ShopForm


class ShopUpdate(UpdateView):
    model = Shop
    form_class = ShopForm

import json

from django.core.serializers.json import DjangoJSONEncoder
from django.http import HttpResponse

from .models import XpJpyRate


def xp2jpy_rate(request):
    rate_rec = XpJpyRate.objects.get_latest()
    rate_dict = {
        'price_jpy': rate_rec.price_jpy,
        'last_updated': rate_rec.last_updated,
    }
    rate = []
    rate.append(rate_dict)
    return HttpResponse(json.dumps(rate, cls=DjangoJSONEncoder), content_type='application/json')

from django.db import models
from django.utils import timezone

from .utils import xp2jpy


class RateManager(models.Manager):

    def get_latest(self):
        try:
            last_rate = self.latest()
        except models.ObjectDoesNotExist:
            last_rate = None
        if last_rate and timezone.now() - last_rate.last_updated < timezone.timedelta(minutes=5):
            return last_rate
        else:
            new_rate = xp2jpy()
            updated_at = timezone.make_aware(
                timezone.datetime.utcfromtimestamp(int(new_rate['last_updated'])), timezone.utc
            )
            new_record = self.create(price_jpy=new_rate['price_jpy'], last_updated=updated_at)
            new_record.save()
            return self.latest()


class XpJpyRate(models.Model):
    price_jpy = models.DecimalField(verbose_name='1XPのJPYでの価格', max_digits=15, decimal_places=10)
    last_updated = models.DateTimeField(verbose_name='最終更新日時')
    created_at = models.DateTimeField(verbose_name='作成日時', auto_now_add=True)
    objects = RateManager()

    class Meta:
        get_latest_by = 'last_updated'

    def __str__(self):
        return f'1XP={self.price_jpy}JPY @{self.last_updated}'

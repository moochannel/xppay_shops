from django.db import models
from django.urls import reverse
from django.utils import timezone


class Area(models.Model):
    name = models.CharField(max_length=20)
    list_order = models.IntegerField()

    def __str__(self):
        return self.name


class Shop(models.Model):
    area = models.ForeignKey(
        Area, verbose_name='地域', on_delete=models.PROTECT, related_name='shops'
    )
    name = models.CharField(verbose_name='店舗名', max_length=200)
    business_description = models.CharField(verbose_name='紹介文', max_length=1000)
    zipcode = models.CharField(
        verbose_name='郵便番号', max_length=7, help_text='ハイフンを入れず7桁の数字で入力してください'
    )
    address1 = models.CharField(verbose_name='住所1', max_length=100)
    address2 = models.CharField(verbose_name='住所2', max_length=100, blank=True)
    map_url = models.URLField(verbose_name='店舗地図URL', max_length=2000, blank=True)

    def get_absolute_url(self):
        return reverse('shop_detail', kwargs={'pk': self.pk})

    def benefits_available(self, when=None):
        if when:
            basis_dt = when
            if timezone.is_naive(when):
                basis_dt = timezone.make_aware(basis_dt, timezone.get_current_timezone())
        else:
            basis_dt = timezone.now()

        return self.benefit_set.filter(
            models.Q(starts_at__lte=basis_dt),
            (models.Q(ends_at__isnull=True) | models.Q(ends_at__gte=basis_dt))
        ).order_by('-ends_at', '-starts_at')


class ContactType(models.Model):
    name = models.CharField(max_length=10)


class Contact(models.Model):
    shop = models.ForeignKey(Shop, on_delete=models.CASCADE)
    list_order = models.IntegerField()
    contact_type = models.ForeignKey(ContactType, on_delete=models.PROTECT)
    label = models.CharField(max_length=100)
    href = models.CharField(max_length=300, blank=True, null=True)


class Benefit(models.Model):
    shop = models.ForeignKey(Shop, on_delete=models.CASCADE)
    content = models.CharField(max_length=200)
    starts_at = models.DateTimeField(auto_now_add=True)
    ends_at = models.DateTimeField(blank=True, null=True)

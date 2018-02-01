from django.db import models
from django.utils import timezone


class Area(models.Model):
    name = models.CharField(max_length=20)
    list_order = models.IntegerField()


class Shop(models.Model):
    area = models.ForeignKey(Area, on_delete=models.PROTECT, related_name='shops')
    name = models.CharField(max_length=200)
    business_description = models.CharField(max_length=1000)
    zipcode = models.CharField(max_length=7)
    address1 = models.CharField(max_length=100)
    address2 = models.CharField(max_length=100, blank=True)
    map_url = models.URLField(blank=True)

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

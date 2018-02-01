from django.db import models


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


class ContactType(models.Model):
    name = models.CharField(max_length=10)


class Contact(models.Model):
    shop = models.ForeignKey(Shop, on_delete=models.CASCADE)
    list_order = models.IntegerField()
    contact_type = models.ForeignKey(ContactType, on_delete=models.PROTECT)
    label = models.CharField(max_length=100)
    href = models.CharField(max_length=300, blank=True, null=True)

from django.db import models


class ActiveWebhookManager(models.Manager):

    def get_queryset(self):
        return super().get_queryset().filter(models.Q(enabled=True),)


class Webhook(models.Model):
    excerpt = models.CharField(verbose_name='表示名', max_length=255)
    url = models.URLField(verbose_name='Webhook URL', max_length=2000)
    enabled = models.BooleanField(verbose_name='使用中', default=True)

    objects = models.Manager()
    active_objects = ActiveWebhookManager()

    def __str__(self):
        return f'Webhook - {self.excerpt}'

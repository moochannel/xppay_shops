from django.contrib.auth.models import AbstractUser
from django.db import models
from django.urls import reverse


class User(AbstractUser):
    discord_id = models.BigIntegerField(null=True)
    avatar_hash = models.CharField(max_length=64, blank=True)

    def get_absolute_url(self):
        return reverse('accounts:profile_edit')

from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    discord_id = models.BigIntegerField(null=True)
    avatar_hash = models.CharField(max_length=64, blank=True)

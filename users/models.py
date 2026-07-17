from django.db import models
from django.contrib.auth.models import User

from promyvki.models import CompressorStation


class UserProfile(models.Model):

    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        verbose_name="Пользователь"
    )

    station = models.ForeignKey(
        CompressorStation,
        on_delete=models.CASCADE,
        verbose_name="Компрессорная станция"
    )

    def __str__(self):
        return f"{self.user.username} ({self.station.name})"
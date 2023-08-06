from django.db import models

from core_models.app.models.base import BaseModelAbstract


class Currency(BaseModelAbstract, models.Model):
    name = models.CharField(max_length=100, unique=True, null=False, blank=False)
    code = models.CharField(max_length=5, unique=True, null=False, blank=False)
    symbol = models.CharField(max_length=5, null=False, blank=False)
    active = models.BooleanField(default=True)

    class Meta:
        verbose_name_plural = "Currencies"
        ordering = ('name', )

    def __unicode__(self):
        return f"{self.name}|{self.code}|{self.symbol}"

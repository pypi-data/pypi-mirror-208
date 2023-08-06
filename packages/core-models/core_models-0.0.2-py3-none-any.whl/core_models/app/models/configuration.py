from django.db import models

from core_models import constants
from core_models.app.models import User


class Configuration(models.Model):
    liquify_fee = models.DecimalField(max_digits=15, decimal_places=2)
    liquify_fee_type = models.CharField(max_length=1, choices=constants.LIQUIFY_FEE_TYPES)
    last_updated_by = models.ForeignKey(User, models.SET_NULL, null=True, blank=True)
    last_updated_on = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Configuration #{self.pk}"

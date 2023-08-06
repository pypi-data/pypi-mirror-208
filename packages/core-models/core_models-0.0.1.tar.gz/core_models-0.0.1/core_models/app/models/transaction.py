from django.db import models

from .base import BaseModelAbstract
from .invoice import Invoice
from ... import constants


class Transaction(BaseModelAbstract, models.Model):
    invoice = models.ForeignKey(Invoice, models.CASCADE)
    amount = models.DecimalField(decimal_places=2, max_digits=30)
    fees = models.DecimalField(decimal_places=2, max_digits=30)
    total = models.DecimalField(decimal_places=2, max_digits=30)
    reference = models.CharField(max_length=100, )
    full_payment = models.BooleanField(default=False)
    status = models.CharField(max_length=30, choices=constants.TXN_STATUSES,
                              default=constants.PENDING_TXN_STATUS)
    gateway = models.CharField(max_length=30, null=True, blank=True)
    gateway_response = models.TextField(blank=True, null=True)

    def __unicode__(self):
        return self.reference

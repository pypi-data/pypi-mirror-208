from django.db import models
from django.utils import timezone
from core_models import constants
from core_models.app.models import User, Currency
from .base import BaseModelAbstract


class Invoice(BaseModelAbstract, models.Model):
    seller = models.ForeignKey(User, models.SET_NULL, null=True, blank=True, related_name='sent_invoices')
    buyer = models.ForeignKey(User, models.SET_NULL, null=True, blank=True, related_name='received_invoices')
    financier = models.ForeignKey(User, models.SET_NULL, null=True, blank=True, related_name='funded_invoices')
    currency = models.ForeignKey(Currency, models.SET_NULL, null=True, blank=True)
    reference = models.CharField(max_length=20, null=True, blank=True, editable=False)
    invoice_number = models.CharField(max_length=50, null=False, blank=False)
    subtotal = models.DecimalField(decimal_places=2, max_digits=30, null=False, blank=False)
    total = models.DecimalField(decimal_places=2, max_digits=30, null=False, blank=False)
    tax = models.DecimalField(decimal_places=2, max_digits=30, null=False, blank=False)
    invoice_date = models.DateField(null=False, blank=False)
    due_date = models.DateField(null=False, blank=False)
    note = models.TextField(null=True, blank=True)
    status = models.CharField(max_length=30, choices=constants.INVOICE_STATUSES,
                              default=constants.NEW_INVOICE_STATUS)
    recurring = models.BooleanField(default=False)
    draft = models.BooleanField(default=False)
    seller_risk_percentage = models.FloatField(default=0)
    buyer_risk_percentage = models.FloatField(default=0)
    base_rate = models.FloatField(default=0)
    interest_rate = models.FloatField(default=0, editable=False)
    interest = models.DecimalField(decimal_places=2, max_digits=30)
    liquify_fee = models.DecimalField(decimal_places=2, max_digits=30, default=0)
    buyer_amount = models.DecimalField(decimal_places=2, max_digits=30, default=0)
    seller_amount = models.DecimalField(decimal_places=2, max_digits=30, default=0)
    financier_amount = models.DecimalField(decimal_places=2, max_digits=30, default=0)

    def save(self, keep_deleted=False, **kwargs):
        if not self.reference:
            now = timezone.now()
            self.reference = f"LQIN{now.strftime('%Y%m%d%H%M%S')}"
        if self.base_rate and self.seller_risk_percentage and self.buyer_risk_percentage:
            self.interest_rate = sum([self.base_rate, self.seller_risk_percentage, self.buyer_risk_percentage])
            self.interest = round(self.total * self.interest_rate, 2)
            self.buyer_amount = self.total
            self.financier_amount = self.total - self.interest
            self.seller_amount = self.financier_amount - self.liquify_fee
        super(Invoice, self).save(keep_deleted, **kwargs)

    def __unicode__(self):
        return self.reference


class InvoiceItem(BaseModelAbstract, models.Model):
    invoice = models.ForeignKey(Invoice, models.CASCADE, related_name="items")
    description = models.TextField(null=False, blank=False)
    amount = models.DecimalField(decimal_places=2, max_digits=20)
    quantity = models.DecimalField(default=1, decimal_places=2, max_digits=10)

    def __unicode__(self):
        return f"{self.invoice} item"

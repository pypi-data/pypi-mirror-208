from django.db import models

from .base import BaseModelAbstract


class BankAccount(BaseModelAbstract, models.Model):
    bank_name = models.CharField(max_length=255)
    account_number = models.CharField(max_length=255)
    sort_code = models.CharField(max_length=20)

    def __unicode__(self):
        return f"{self.bank_name}|{self.account_number}|{self.sort_code}"

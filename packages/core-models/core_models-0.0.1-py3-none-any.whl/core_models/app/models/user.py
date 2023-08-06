from django.contrib.auth.models import AbstractUser
from django.db import models

from .base import BaseModelAbstract
from core_models.constants import USER_TYPES
from ... import constants


class User(AbstractUser, BaseModelAbstract):
    """
        Overrides django's default auth model
    """
    USERNAME_FIELD = "email"
    username = None
    REQUIRED_FIELDS = ["first_name", "last_name", "phone_number", "user_type"]
    
    email = models.EmailField(unique=True, null=False, blank=False)
    job_role = models.CharField(max_length=100, blank=True, null=True)
    phone_number = models.CharField(max_length=25, blank=True, null=True)
    email_verified = models.BooleanField(default=False)
    user_type = models.CharField(max_length=15, choices=USER_TYPES)
    is_onboarding_complete = models.BooleanField(default=False)
    onboarding_stage = models.IntegerField(default=1)
    reset_token = models.CharField(max_length=10, null=True, blank=True)
    reset_token_expiry = models.DateTimeField(null=True, blank=True)
    notification_tokens = models.JSONField(blank=True, null=True)

    def buyers(self):
        return self.seller_contracts.filter(
            status__in=(
                constants.ACCEPTED_CONTRACT_STATUS,
                constants.VERIFIED_CONTRACT_STATUS
            )
        )

    def sellers(self):
        return self.buyer_contracts.filter(
            status__in=(
                constants.ACCEPTED_CONTRACT_STATUS,
                constants.VERIFIED_CONTRACT_STATUS
            )
        )

    @property
    def user_type_description(self):
        return constants.USER_TYPES_MAP.get(self.user_type, 'None')

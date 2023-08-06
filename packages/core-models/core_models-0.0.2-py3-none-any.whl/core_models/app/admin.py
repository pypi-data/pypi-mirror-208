from django.contrib import admin
from safedelete import HARD_DELETE

from .models import *
from django.contrib.auth import get_user_model
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin


class CompanyInline(admin.StackedInline):
    model = Company
    can_delete = False
    fk_name = 'user'


class BankAccountInline(admin.TabularInline):
    model = BankAccount
    can_delete = False
    fk_name = 'created_by'


class UserAdmin(BaseUserAdmin):
    inlines = (CompanyInline, BankAccountInline)
    fieldsets = (
        (None, {"fields": ("email", "password")}),
        ("Personal info", {"fields": ("first_name", "last_name", "job_role", "phone_number", "onboarding_stage", "is_onboarding_complete", "notification_tokens")}),
        (
            "Permissions",
            {
                "fields": (
                    "is_active",
                    "is_staff",
                    "is_superuser",
                    "user_type",
                    "email_verified"
                ),
            },
        ),
        ("Important dates", {"fields": ("last_login", "date_joined")}),
    )
    add_fieldsets = (
        (
            None,
            {
                "classes": ("wide",),
                "fields": ("email", "first_name", "last_name", "password1", "password2"),
            },
        ),
    )
    list_display = ("email", "first_name", "last_name", "phone_number", "job_role", "user_type", "is_staff", "is_superuser")
    list_filter = ("user_type", "is_staff", "is_superuser", "is_active")
    search_fields = ("email", "first_name", "last_name", "phone_number")
    ordering = ("email", "first_name", "last_name", "phone_number", "created_at")

    def get_queryset(self, request):
        qs = self.model.all_objects.get_queryset()
        # TODO: this should be handled by some parameter to the ChangeList.
        ordering = self.get_ordering(request)
        if ordering:
            qs = qs.order_by(*ordering)
        return qs

    def delete_model(self, request, obj):
        """
        Given a model instance delete it from the database.
        """
        obj.delete(force_policy=HARD_DELETE)

    def delete_queryset(self, request, queryset):
        """Given a queryset, delete it from the database."""
        queryset.delete(force_policy=HARD_DELETE)


class CompanyDocumentInline(admin.TabularInline):
    model = CompanyDocument
    can_delete = False
    fk_name = 'company'


class CompanyAdmin(admin.ModelAdmin):
    inlines = (CompanyDocumentInline, )
    list_display = (
        "user", "name", "registration_number",
        "address_line1", "country", "is_verified",
        "date_verified", "created_at", "updated_at", "deleted"
    )
    list_filter = ("is_verified", "country", "deleted")
    search_fields = ("user", "name", "registration_number")
    ordering = ("name", "created_at", "date_verified")

    def get_queryset(self, request):
        qs = self.model.all_objects.get_queryset()
        # TODO: this should be handled by some parameter to the ChangeList.
        ordering = self.get_ordering(request)
        if ordering:
            qs = qs.order_by(*ordering)
        return qs

    def delete_model(self, request, obj):
        """
        Given a model instance delete it from the database.
        """
        obj.delete(force_policy=HARD_DELETE)

    def delete_queryset(self, request, queryset):
        """Given a queryset, delete it from the database."""
        queryset.delete(force_policy=HARD_DELETE)


class ContractDocumentItemInline(admin.TabularInline):
    model = ContractDocument
    can_delete = False
    fk_name = 'contract'


class ContractDocumentItemInline(admin.TabularInline):
    model = ContractStatusLog
    can_delete = False
    fk_name = 'contract'


class ContractAdmin(admin.ModelAdmin):
    inlines = (ContractDocumentItemInline, ContractDocumentItemInline)
    list_display = (
        "reference", "seller", "buyer", "document",
        "status", "buyer_accepted_on", "buyer_accepted_via",
        "created_at", "updated_at", "deleted"
    )
    list_filter = ("status", )
    search_fields = ("reference", "seller", "buyer")
    ordering = ("reference", "created_at", "buyer_accepted_on")

    def get_queryset(self, request):
        qs = self.model.all_objects.get_queryset()
        # TODO: this should be handled by some parameter to the ChangeList.
        ordering = self.get_ordering(request)
        if ordering:
            qs = qs.order_by(*ordering)
        return qs

    def delete_model(self, request, obj):
        """
        Given a model instance delete it from the database.
        """
        obj.delete(force_policy=HARD_DELETE)

    def delete_queryset(self, request, queryset):
        """Given a queryset, delete it from the database."""
        queryset.delete(force_policy=HARD_DELETE)


class BankAccountAdmin(admin.ModelAdmin):
    list_display = (
        "created_by", "bank_name", "account_number", "sort_code",
        "created_at", "updated_at", "deleted"
    )
    search_fields = ("created_by", "account_number")
    ordering = ("bank_name", "created_at")

    def get_queryset(self, request):
        qs = self.model.all_objects.get_queryset()
        # TODO: this should be handled by some parameter to the ChangeList.
        ordering = self.get_ordering(request)
        if ordering:
            qs = qs.order_by(*ordering)
        return qs

    def delete_model(self, request, obj):
        """
        Given a model instance delete it from the database.
        """
        obj.delete(force_policy=HARD_DELETE)

    def delete_queryset(self, request, queryset):
        """Given a queryset, delete it from the database."""
        queryset.delete(force_policy=HARD_DELETE)


class CurrencyAdmin(admin.ModelAdmin):
    list_display = (
        "created_by", "name", "code", "symbol", "created_at", "updated_at", "deleted"
    )
    search_fields = ("code", "name", "symbol")
    ordering = ("name", "created_at")

    def get_queryset(self, request):
        qs = self.model.all_objects.get_queryset()
        # TODO: this should be handled by some parameter to the ChangeList.
        ordering = self.get_ordering(request)
        if ordering:
            qs = qs.order_by(*ordering)
        return qs

    def save_model(self, request, obj, form, change):
        if not change:
            obj.created_by = request.user
        super(CurrencyAdmin, self).save_model(request, obj, form, change)

    def delete_model(self, request, obj):
        """
        Given a model instance delete it from the database.
        """
        obj.delete(force_policy=HARD_DELETE)

    def delete_queryset(self, request, queryset):
        """Given a queryset, delete it from the database."""
        queryset.delete(force_policy=HARD_DELETE)


class InvoiceItemInline(admin.TabularInline):
    model = InvoiceItem
    can_delete = False
    fk_name = 'invoice'
    extra = 0


class TransactionInline(admin.TabularInline):
    model = Transaction
    can_delete = False
    fk_name = 'invoice'
    extra = 0


class InvoiceAdmin(admin.ModelAdmin):
    inlines = (InvoiceItemInline, TransactionInline)
    list_display = (
        "seller", "buyer", "financier", "currency", "reference",
        "invoice_number", "total", "interest_rate", "status", "invoice_date", "due_date",
        "created_at", "recurring", "deleted"
    )
    search_fields = ("reference", "invoice_number")
    ordering = ("reference", "total", "invoice_date", "due_date")
    list_filter = ("deleted", "recurring", "status")

    def get_queryset(self, request):
        qs = self.model.all_objects.get_queryset()
        # TODO: this should be handled by some parameter to the ChangeList.
        ordering = self.get_ordering(request)
        if ordering:
            qs = qs.order_by(*ordering)
        return qs

    def save_model(self, request, obj, form, change):
        if not change:
            obj.created_by = request.user
        super(InvoiceAdmin, self).save_model(request, obj, form, change)

    def delete_model(self, request, obj):
        """
        Given a model instance delete it from the database.
        """
        obj.delete(force_policy=HARD_DELETE)

    def delete_queryset(self, request, queryset):
        """Given a queryset, delete it from the database."""
        queryset.delete(force_policy=HARD_DELETE)


class ConfigurationAdmin(admin.ModelAdmin):
    list_display = (
        "liquify_fee", "liquify_fee_type",
        "last_updated_by", "last_updated_on"
    )

    def has_delete_permission(self, request, obj=None):
        return False

    def has_add_permission(self, request):
        count = Configuration.objects.count()
        return count == 0

    def save_model(self, request, obj, form, change):
        obj.last_updated_by = request.user
        super(ConfigurationAdmin, self).save_model(request, obj, form, change)


User_ = get_user_model()

admin.site.register(User_, UserAdmin)
admin.site.register(Company, CompanyAdmin)
admin.site.register(Contract, ContractAdmin)
admin.site.register(BankAccount, BankAccountAdmin)
admin.site.register(Notification)
admin.site.register(Currency, CurrencyAdmin)
admin.site.register(Invoice, InvoiceAdmin)
admin.site.register(Configuration, ConfigurationAdmin)

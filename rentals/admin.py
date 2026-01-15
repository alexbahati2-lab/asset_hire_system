# rentals/admin.py
from django.contrib import admin
from django import forms
from .models import Person, Asset, Hire, Payment

# -----------------------------
# PERSON ADMIN
# -----------------------------
@admin.register(Person)
class PersonAdmin(admin.ModelAdmin):
    list_display = ('full_name', 'national_id', 'unique_id', 'phone', 'email')
    search_fields = ('full_name', 'national_id', 'unique_id', 'phone')
    ordering = ('full_name',)


# -----------------------------
# ASSET ADMIN
# -----------------------------
@admin.register(Asset)
class AssetAdmin(admin.ModelAdmin):
    list_display = ('name', 'brand', 'registration_number', 'status')
    search_fields = ('name', 'brand', 'registration_number')
    list_filter = ('status',)


# -----------------------------
# HIRE ADMIN
# -----------------------------
class HireAdminForm(forms.ModelForm):
    class Meta:
        model = Hire
        fields = '__all__'

    def clean_asset(self):
        asset = self.cleaned_data['asset']
        # Prevent assigning an already assigned asset on create
        if not self.instance.pk and asset.status == 'assigned':
            raise forms.ValidationError("This asset is already assigned.")
        return asset


@admin.register(Hire)
class HireAdmin(admin.ModelAdmin):
    form = HireAdminForm

    list_display = (
        'reference_id',  # Show unique ID
        'person',
        'asset',
        'daily_rate',
        'status',
        'hire_date',
        'due_datetime',
    )
    list_filter = ('status', 'due_datetime')
    search_fields = (
        'reference_id',
        'person__full_name',
        'asset__registration_number',
    )
    ordering = ('-hire_date',)

    readonly_fields = ('reference_id',)  # Don't allow editing

    def get_readonly_fields(self, request, obj=None):
        # Always prevent editing reference_id and asset after creation
        if obj:
            return ('reference_id', 'asset')
        return ('reference_id',)


# -----------------------------
# PAYMENT ADMIN
# -----------------------------
@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = (
        'hire_reference',  # Show hire's reference
        'hire',
        'amount',
        'status',
        'mpesa_receipt',
        'paid_at',
    )
    list_filter = ('status', 'paid_at')
    search_fields = ('mpesa_receipt', 'phone', 'hire_reference')
    readonly_fields = ('mpesa_receipt', 'paid_at', 'hire_reference')
    ordering = ('-paid_at',)

from django.contrib import admin
from django import forms
from .models import Person, Asset, Hire, Payment

# -----------------------------
# PERSON ADMIN
# -----------------------------
@admin.register(Person)
class PersonAdmin(admin.ModelAdmin):
    list_display = ('full_name', 'national_id', 'phone', 'email')
    search_fields = ('full_name', 'national_id', 'phone')
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
        'id',
        'person',
        'asset',
        'daily_rate',
        'status',
        'due_datetime',
    )
    list_filter = ('status', 'due_datetime')
    search_fields = (
        'person__full_name',
        'asset__registration_number',
    )
    ordering = ('-hire_date',)

    def get_readonly_fields(self, request, obj=None):
        # Prevent changing asset after creation
        if obj:
            return ('asset',)
        return ()


# -----------------------------
# PAYMENT ADMIN
# -----------------------------
@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = (
        'hire',
        'amount',
        'status',
        'mpesa_receipt',
        'paid_at',
    )
    list_filter = ('status', 'paid_at')
    search_fields = ('mpesa_receipt', 'phone')
    readonly_fields = ('mpesa_receipt', 'paid_at')
    ordering = ('-paid_at',)

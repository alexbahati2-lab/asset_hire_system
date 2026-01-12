from django.db import models
from django.utils import timezone
import uuid


# -----------------------------
# PERSON (HIRER)
# -----------------------------
class Person(models.Model):
    full_name = models.CharField(max_length=200)
    national_id = models.CharField(max_length=50, unique=True)
    unique_id = models.CharField(
        max_length=50, blank=True, null=True, unique=True
    )
    phone = models.CharField(max_length=20)
    email = models.EmailField(blank=True, null=True)

    def __str__(self):
        return f"{self.full_name} ({self.national_id})"


# -----------------------------
# ASSET
# -----------------------------
class Asset(models.Model):
    STATUS_CHOICES = [
        ('available', 'Available'),
        ('assigned', 'Assigned'),
        ('repossessed', 'Repossessed'),
    ]

    name = models.CharField(max_length=100)
    brand = models.CharField(max_length=100)
    registration_number = models.CharField(max_length=100, unique=True)
    status = models.CharField(
        max_length=20, choices=STATUS_CHOICES, default='available'
    )

    def __str__(self):
        return f"{self.name} - {self.registration_number}"


# -----------------------------
# HIRE (USAGE RECORD)
# -----------------------------
class Hire(models.Model):
    STATUS_CHOICES = [
        ('active', 'Active'),
        ('paid', 'Paid'),
        ('overdue', 'Overdue'),
        ('repossessed', 'Repossessed'),
    ]

    person = models.ForeignKey(Person, on_delete=models.PROTECT)
    asset = models.ForeignKey(Asset, on_delete=models.PROTECT)
    hire_date = models.DateField(default=timezone.now)
    due_datetime = models.DateTimeField()
    daily_rate = models.DecimalField(max_digits=10, decimal_places=2)

    status = models.CharField(
        max_length=20, choices=STATUS_CHOICES, default='active'
    )

    # 🔑 AUTO-GENERATED PAYMENT REFERENCE
    reference_id = models.CharField(
        max_length=12, unique=True, editable=False, blank=True
    )

    def save(self, *args, **kwargs):
        # Generate unique reference ID once
        if not self.reference_id:
            self.reference_id = uuid.uuid4().hex[:12].upper()

        # Asset status handling
        if self.status in ['active', 'paid']:
            self.asset.status = 'assigned'
            self.asset.save()

        if self.status in ['overdue', 'repossessed']:
            self.asset.status = 'repossessed'
            self.asset.save()

        super().save(*args, **kwargs)

    def __str__(self):
        return f"Hire {self.reference_id} - {self.person.full_name}"


# -----------------------------
# PAYMENT (M-PESA)
# -----------------------------
class Payment(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('success', 'Success'),
        ('failed', 'Failed'),
    ]

    hire = models.ForeignKey(
        Hire, on_delete=models.PROTECT, related_name='payments'
    )

    amount = models.DecimalField(max_digits=10, decimal_places=2)
    phone = models.CharField(max_length=20)

    mpesa_receipt = models.CharField(
        max_length=100, blank=True, null=True, unique=True
    )

    status = models.CharField(
        max_length=20, choices=STATUS_CHOICES, default='pending'
    )

    paid_at = models.DateTimeField(blank=True, null=True)

    # 🔗 STORED FOR QUICK LOOKUP & CALLBACK MATCHING
    hire_reference = models.CharField(
        max_length=12, editable=False, blank=True
    )

    def save(self, *args, **kwargs):
        # Auto-copy hire reference
        if self.hire and not self.hire_reference:
            self.hire_reference = self.hire.reference_id

        # Auto-set paid time on success
        if self.status == 'success' and not self.paid_at:
            self.paid_at = timezone.now()

            # Mark hire as paid
            self.hire.status = 'paid'
            self.hire.save()

        super().save(*args, **kwargs)

    def __str__(self):
        return f"Payment {self.hire_reference} - {self.amount} ({self.status})"

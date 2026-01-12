from django.db import models
from django.utils import timezone


# -----------------------------
# PERSON (HIRER)
# -----------------------------
class Person(models.Model):
    full_name = models.CharField(max_length=200)
    national_id = models.CharField(max_length=50, unique=True)  # MUST HAVE
    unique_id = models.CharField(
        max_length=50, blank=True, null=True, unique=True
    )  # OPTIONAL (internal / card / tag)
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

    def save(self, *args, **kwargs):
        # Assign asset when hire is active or paid
        if self.status in ['active', 'paid']:
            self.asset.status = 'assigned'
            self.asset.save()

        # Repossess asset
        if self.status in ['overdue', 'repossessed']:
            self.asset.status = 'repossessed'
            self.asset.save()

        super().save(*args, **kwargs)

    def __str__(self):
        return f"Hire #{self.id} - {self.person.full_name}"



# -----------------------------
# PAYMENT (M-PESA)
# -----------------------------
class Payment(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('success', 'Success'),
        ('failed', 'Failed'),
    ]

    hire = models.ForeignKey(Hire, on_delete=models.PROTECT, related_name='payments')
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    phone = models.CharField(max_length=20)
    mpesa_receipt = models.CharField(
        max_length=100, blank=True, null=True, unique=True
    )
    status = models.CharField(
        max_length=20, choices=STATUS_CHOICES, default='pending'
    )
    paid_at = models.DateTimeField(blank=True, null=True)

    def __str__(self):
        return f"Payment {self.amount} - {self.status}"

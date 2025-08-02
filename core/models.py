from datetime import date
from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator, MinLengthValidator
from django.utils import timezone
class Address(models.Model):
    street = models.CharField(max_length=255, validators=[MinLengthValidator(2)])
    street_number = models.CharField(max_length=20)
    city_code = models.CharField(max_length=20, db_index=True)
    city = models.CharField(max_length=100, validators=[MinLengthValidator(2)])
    country = models.CharField(max_length=100, validators=[MinLengthValidator(2)])

    class Meta:
        indexes = [
            models.Index(fields=["city_code"]),
            models.Index(fields=["city", "country"]),
        ]

    def __str__(self):
        return f"{self.street} {self.street_number}, {self.city}, {self.country}"


class AppUser(models.Model):
    GENDER_CHOICES = [
        ("Male", "Male"),
        ("Female", "Female"),
        ("Other", "Other"),
        ("Prefer not to say", "Prefer not to say"),
    ]

    first_name = models.CharField(max_length=100, db_index=True, validators=[MinLengthValidator(2)])
    last_name = models.CharField(max_length=100, db_index=True, validators=[MinLengthValidator(2)])
    gender = models.CharField(max_length=20, choices=GENDER_CHOICES)
    customer_id = models.CharField(max_length=50, unique=True)
    phone_number = models.CharField(max_length=20, blank=True, null=True)
    created = models.DateTimeField(default=timezone.now)
    address = models.ForeignKey(Address, on_delete=models.CASCADE, related_name="users")
    birthday = models.DateField(
        blank=True,
        null=True,
        db_index=True,
        validators=[
            MinValueValidator(
                limit_value=date(1900, 1, 1),
                message="Birthday cannot be before 1900"
            ),
            MaxValueValidator(
                limit_value=date.today(),
                message="Birthday cannot be in the future"
            )
        ]
    )
    last_updated = models.DateTimeField(auto_now=True)

    class Meta:
        indexes = [
            models.Index(fields=["first_name"]),
            models.Index(fields=["last_name"]),
            models.Index(fields=["customer_id"]),
            models.Index(fields=["created"]),
            models.Index(fields=["address"]),
            models.Index(fields=["birthday"]),
        ]
        ordering = ["-created"]

    def __str__(self):
        return f"{self.first_name} {self.last_name}"


class CustomerRelationship(models.Model):
    appuser = models.ForeignKey(AppUser, on_delete=models.CASCADE, related_name="relationships")
    points = models.IntegerField()
    created = models.DateTimeField(default=timezone.now)
    last_activity = models.DateTimeField(blank=True, null=True)

    class Meta:
        indexes = [
            models.Index(fields=["appuser"]),
            models.Index(fields=["created"]),
            models.Index(fields=["last_activity"]),
            models.Index(fields=["points"]),
        ]
        unique_together = [("appuser", "created")]

    def __str__(self):
        return f"User: {self.appuser_id}, Points: {self.points}"

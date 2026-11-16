from django.contrib.auth.models import AbstractUser
from django.core.validators import RegexValidator
from django.db import models


class User(AbstractUser):
    class Role(models.TextChoices):
        MEMBER = 'member', 'Member'
        ADMIN = 'admin', 'Admin'

    email = models.EmailField(unique=True)
    role = models.CharField(max_length=10, choices=Role.choices, default=Role.MEMBER)
    contact_number = models.CharField(
        max_length=15,
        blank=True,
        validators=[RegexValidator(r'^\+?\d{7,15}$', 'Enter a valid contact number (7-15 digits).')],
    )
    profile_photo = models.ImageField(upload_to='profile_photos/', blank=True, null=True)

    def save(self, *args, **kwargs):
        # Superusers made with createsuperuser are always Admins
        if self.is_superuser:
            self.role = self.Role.ADMIN
        super().save(*args, **kwargs)

    def __str__(self):
        return self.username
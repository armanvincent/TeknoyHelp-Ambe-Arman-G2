from decimal import Decimal

from django.conf import settings
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
from django.urls import reverse


class Category(models.Model):
    name = models.CharField(max_length=50, unique=True)

    class Meta:
        verbose_name_plural = 'categories'
        ordering = ['name']

    def __str__(self):
        return self.name


class ErrandRequest(models.Model):
    class Status(models.TextChoices):
        OPEN = 'open', 'Open'
        ACCEPTED = 'accepted', 'In progress'
        COMPLETED = 'completed', 'Awaiting confirmation'
        CONFIRMED = 'confirmed', 'Reward confirmed'

    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='posted_errands'
    )
    taker = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL,
        null=True, blank=True, related_name='accepted_errands'
    )
    category = models.ForeignKey(Category, on_delete=models.PROTECT, related_name='errands')
    title = models.CharField(max_length=120)
    description = models.TextField()
    location = models.CharField(max_length=150)
    deadline = models.DateTimeField()
    reward = models.DecimalField(
        max_digits=8, decimal_places=2,
        validators=[MinValueValidator(Decimal('1.00')), MaxValueValidator(Decimal('10000.00'))],
    )
    status = models.CharField(max_length=10, choices=Status.choices, default=Status.OPEN)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    accepted_at = models.DateTimeField(null=True, blank=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    confirmed_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse('errand_detail', args=[self.pk])

    @property
    def badge_class(self):
        return {
            'open': 'success',
            'accepted': 'primary',
            'completed': 'info',
            'confirmed': 'dark',
        }[self.status]
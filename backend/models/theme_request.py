from django.db import models
from backend.models import User

class ThemeRequest(models.Model):
    """A user request to add a new theme."""

    STATUS_CHOICES = [
        ('pending',  'Pending'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
    ]

    requested_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='theme_requests')
    title = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    reason = models.TextField()
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='pending')
    date_created = models.DateTimeField(auto_now_add=True)
    reviewed_at = models.DateTimeField(null=True, blank=True)
from django.db import models
from django.conf import settings  # important for custom user models

class Complaint(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,  # works even with custom user models
        on_delete=models.CASCADE
    )
    message = models.TextField()
    submitted_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Complaint from {self.user} - {self.submitted_at.strftime('%Y-%m-%d %H:%M')}"

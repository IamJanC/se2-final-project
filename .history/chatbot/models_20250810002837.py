from django.db import models
from django.conf import settings  # use settings for custom user models

class Complaint(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,  # works with custom or default User
        on_delete=models.CASCADE
    )
    message = models.TextField()
    submitted_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Complaint from {self.user} - {self.submitted_at.strftime('%Y-%m-%d %H:%M')}"

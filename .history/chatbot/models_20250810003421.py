from django.db import models
from django.conf import settings  # ✅ Use custom user model dynamically

class Complaint(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    message = models.TextField()
    submitted_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Complaint from {self.user.username} - {self.submitted_at.strftime('%Y-%m-%d %H:%M')}"

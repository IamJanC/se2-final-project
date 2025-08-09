from django.db import models
from django.contrib.auth.models import User  # new import

class Complaint(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)  # link to logged-in user
    message = models.TextField()
    submitted_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Complaint from {self.user.username} - {self.submitted_at.strftime('%Y-%m-%d %H:%M')}"

from django.db import models
from django.contrib.auth.models import User

class Complaint(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)  # link to who sent it
    message = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Complaint from {self.user.username} at {self.created_at:%Y-%m-%d %H:%M}"

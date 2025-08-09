from django.db import models

class Complaint(models.Model):
    message = models.TextField()
    submitted_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Complaint #{self.id} - {self.submitted_at.strftime('%Y-%m-%d %H:%M')}"

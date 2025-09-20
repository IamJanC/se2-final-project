from django.contrib.auth.models import AbstractUser             # type: ignore
from django.db import models                                    # type: ignore
from cloudinary.models import CloudinaryField  # NEW

class CustomUser(AbstractUser):
    is_admin = models.BooleanField(default=False)
    phone_number = models.CharField(max_length=15, blank=True)
    profile_pic = CloudinaryField("image", blank=True, null=True)  # NEW



from django.contrib.auth.models import AbstractUser             # type: ignore
from django.db import models                                    # type: ignore

class CustomUser(AbstractUser):
    is_admin = models.BooleanField(default=False)
    phone_number = models.CharField(max_length=15, blank=True)




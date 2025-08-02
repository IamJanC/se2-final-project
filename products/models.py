from django.db import models


class Category(models.Model):
    name = models.CharField(max_length=100, unique=True)
    slug = models.SlugField(max_length=100, unique=True)

    def __str__(self):
        return self.name

class Product(models.Model):
    name = models.CharField(max_length=100)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    description = models.TextField()
    stock = models.IntegerField()
    image_url = models.URLField(blank=True, null=True)  # New field
    category = models.ForeignKey(Category, on_delete=models.CASCADE)  # New field

    def __str__(self):
        return self.name
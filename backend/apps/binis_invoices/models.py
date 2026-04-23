from django.db import models

# Create your models here.
class Order(models.Model):
    id = models.AutoField(primary_key=True)
    client = models.CharField(max_length=40)
    date = models.DateField()
    price = models.CharField()

class Brand(models.Model):
    id = models.AutoField(primary_key=True)
    brand_full = models.CharField(max_length=30, unique=True)
    brand_display = models.CharField(max_length=30)
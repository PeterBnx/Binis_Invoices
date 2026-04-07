from django.db import models

# Create your models here.
class Order(models.Model):
    id = models.AutoField(primary_key=True)
    client = models.CharField(max_length=40)
    date = models.DateField()
    status = models.CharField()
from django.db import models

# Create your models here.
class Patient(models.Model):
    patient_id = models.BigAutoField(primary_key=True)
    first_name= models.CharField(max_length=50)
    last_name= models.CharField(max_length=50)
    blood= models.CharField(max_length=50)

    def __str__(self):
        return self.first_name


class Hospital(models.Model):
    hospital_id = models.BigAutoField(primary_key=True)
    name = models.CharField(max_length=100)
    address = models.TextField()
    phone = models.CharField(max_length=20)
    email = models.EmailField(blank=True, null=True)
    capacity = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name

    class Meta:
        ordering = ['name']


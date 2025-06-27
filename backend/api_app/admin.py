from django.contrib import admin
from api_app.models import Patient, Hospital

# Register your models here.
admin.site.register(Patient)
admin.site.register(Hospital)
from rest_framework import serializers
from api_app.models import Patient, Hospital

class PatientSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Patient
        fields = ['patient_id','last_name','first_name','blood'] 

class HospitalSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Hospital
        fields = ['hospital_id', 'name', 'address', 'phone', 'email', 'capacity', 'created_at', 'updated_at'] 
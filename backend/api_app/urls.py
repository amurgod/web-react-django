from django.urls import path, include
from rest_framework.routers import DefaultRouter
from api_app.views import PatientViewSet, HospitalViewSet, login_user, refresh_token

router = DefaultRouter()
router.register(r'patient', PatientViewSet)
router.register(r'hospital', HospitalViewSet)

urlpatterns = [
    path('', include(router.urls)),
    path('login/', login_user, name='login'),
    path('refresh-token/', refresh_token, name='refresh-token'),
]
from django.urls import path
from .views import HealthCheckView, TenantInfoView

urlpatterns = [
    path('health/', HealthCheckView.as_view(), name="health-check"),
    path('salon/', TenantInfoView.as_view(), name='tenant-info'),
]
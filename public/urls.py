from django.urls import path
from .views import (
    HealthCheckView, TenantInfoView, SuperAdminTableauDeBordView,
    SuperAdminActiverView, SuperAdminDebloquerView, SuperAdminDomainCustomView,
    SuperAdminProlongerEssaiView, SuperAdminSuspendreView, SuperAdminTenantDetailView,
    SuperAdminTenantListCreateView, SuperAdminVerifierExpirationsView
)

urlpatterns = [

    # Routes Publiques
    path('health/', HealthCheckView.as_view(), name="health-check"),
    path('salon/', TenantInfoView.as_view(), name='tenant-info'),

    # Routes Super Admin
    path('super-admin/', SuperAdminTableauDeBordView.as_view(), name='super-admin-dashboard'),
    path('super-admin/tenants/', SuperAdminTenantListCreateView.as_view(), name='super-admin-tenants'),
    path('super-admin/tenants/<int:tenant_id>/', SuperAdminTenantDetailView.as_view(), name='super-admin-tenant-detail'),
    path('super-admin/tenants/<int:tenant_id>/activer/', SuperAdminActiverView.as_view(), name='super-admin-activer'),
    path('super-admin/tenants/<int:tenant_id>/suspendre/', SuperAdminSuspendreView.as_view(), name='super-admin-suspendre'),
    path('super-admin/tenants/<int:tenant_id>/debloquer/', SuperAdminDebloquerView.as_view(), name='super-admin-debloquer'),
    path('super-admin/tenants/<int:tenant_id>/prolonger-essai/', SuperAdminProlongerEssaiView.as_view(), name='super-admin-prolonger'),
    path('super-admin/tenants/<int:tenant_id>/domaine-custom/', SuperAdminDomainCustomView.as_view(), name='super-admin-domaine'),
    path('super-admin/verifier-expirations/', SuperAdminVerifierExpirationsView.as_view(), name='super-admin-expirations'),
]
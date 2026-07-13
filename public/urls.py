from django.urls import path
from .views import (
    HealthCheckView, TenantInfoView, SuperAdminTableauDeBordView,
    SuperAdminActiverView, SuperAdminDebloquerView, SuperAdminDomainCustomView,
    SuperAdminProlongerEssaiView, SuperAdminSuspendreView, SuperAdminTenantDetailView,
    SuperAdminTenantListCreateView, SuperAdminVerifierExpirationsView, SuperAdminExpirantBientotView,
    SuperAdminAjouterJoursLicenceView, SuperAdminImpersonnaliserView, SuperAdminJournalPlateformeView,
    SuperAdminJournalTenantView,
)

urlpatterns = [

    # Routes Publiques
    path('health/', HealthCheckView.as_view(), name="health-check"),
    path('salon/', TenantInfoView.as_view(), name='tenant-info'),

    # Routes Super Admin
    path('super-admin/', SuperAdminTableauDeBordView.as_view(), name='super-admin-dashboard'),
    path('super-admin/tenants/', SuperAdminTenantListCreateView.as_view(), name='super-admin-tenants'),
    path('super-admin/tenants/verifier-expirations/', SuperAdminVerifierExpirationsView.as_view(), name='super-admin-expirations'),
    path('super-admin/tenants/expirants-bientot/', SuperAdminExpirantBientotView.as_view(), name='super-admin-expirants-bientot'),
    path('super-admin/tenants/<str:sous_domaine>/', SuperAdminTenantDetailView.as_view(), name='super-admin-tenant-detail'),
    path('super-admin/tenants/<int:tenant_id>/activer/', SuperAdminActiverView.as_view(), name='super-admin-activer'),
    path('super-admin/tenants/<int:tenant_id>/suspendre/', SuperAdminSuspendreView.as_view(), name='super-admin-suspendre'),
    path('super-admin/tenants/<int:tenant_id>/debloquer/', SuperAdminDebloquerView.as_view(), name='super-admin-debloquer'),
    path('super-admin/tenants/<int:tenant_id>/prolonger-essai/', SuperAdminProlongerEssaiView.as_view(), name='super-admin-prolonger'),
    path('super-admin/tenants/<int:tenant_id>/ajouter-jours-licence/', SuperAdminAjouterJoursLicenceView.as_view(), name='super-admin-ajouter-jours-licence'),
    path('super-admin/tenants/<int:tenant_id>/domaine-custom/', SuperAdminDomainCustomView.as_view(), name='super-admin-domaine'),
    path('super-admin/tenants/<str:sous_domaine>/impersonnaliser/', SuperAdminImpersonnaliserView.as_view(), name='super-admin-impersonnaliser'),
    path('super-admin/tenants/<int:tenant_id>/journal/', SuperAdminJournalTenantView.as_view(), name='super-admin-journal-tenant'),
    path('super-admin/journal-plateforme/', SuperAdminJournalPlateformeView.as_view(), name='super-admin-journal-plateforme'),
]
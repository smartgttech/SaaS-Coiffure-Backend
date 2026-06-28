from tenants.models import Tenant, Domain
from django.utils import timezone


class TenantAdminRepository:

    def liste(self, statut=None):
        qs = Tenant.objects.exclude(schema_name='public')
        if statut:
            qs = qs.filter(statut=statut)
        return qs.order_by('-date_creation')

    def par_id(self, tenant_id):
        try:
            return Tenant.objects.exclude(
                schema_name='public'
            ).get(id=tenant_id)
        except Tenant.DoesNotExist:
            return None

    def par_schema(self, schema_name):
        try:
            return Tenant.objects.get(schema_name=schema_name)
        except Tenant.DoesNotExist:
            return None

    def creer(self, data):
        return Tenant(**data)

    def modifier(self, tenant, data):
        for champ, valeur in data.items():
            setattr(tenant, champ, valeur)
        tenant.save()
        return tenant

    def statistiques(self):
        tenants = Tenant.objects.exclude(schema_name='public')
        return {
            'total': tenants.count(),
            'actifs': tenants.filter(statut='actif').count(),
            'en_essai': tenants.filter(statut='essai').count(),
            'suspendus': tenants.filter(statut='suspendu').count(),
            'expires': tenants.filter(statut='expire').count(),
            'expirant_bientot': tenants.filter(
                statut__in=['actif', 'essai'],
                date_expiration__lte=timezone.now() + timezone.timedelta(days=7),
                date_expiration__gte=timezone.now()
            ).count(),
        }


class DomainAdminRepository:

    def creer(self, tenant, domain, is_primary=True):
        return Domain.objects.create(
            tenant=tenant,
            domain=domain,
            is_primary=is_primary
        )

    def par_tenant(self, tenant):
        return Domain.objects.filter(tenant=tenant)

    def domaine_existe(self, domain):
        return Domain.objects.filter(domain=domain).exists()

    def supprimer_custom(self, tenant):
        Domain.objects.filter(
            tenant=tenant,
            is_primary=False
        ).delete()
from django.utils import timezone
from datetime import timedelta
from tenants.models import Tenant
from .repository import TenantAdminRepository, DomainAdminRepository


class SuperAdminService:

    def __init__(self):
        self.tenant_repo = TenantAdminRepository()
        self.domain_repo = DomainAdminRepository()

    def lister_tenants(self, statut=None):
        return self.tenant_repo.liste(statut=statut)

    def obtenir_tenant(self, tenant_id):
        tenant = self.tenant_repo.par_id(tenant_id)
        if tenant is None:
            raise ValueError("Salon introuvable.")
        return tenant

    def statistiques(self):
        return self.tenant_repo.statistiques()

    def creer_tenant(self, data, utilisateur=None):
        schema_name = data['sous_domaine'].lower().replace('-', '_')
        domain_principal = f"{data['sous_domaine']}.monsaas.cm"
        domain_local = f"{data['sous_domaine']}.localhost"

        # Vérifications
        if self.tenant_repo.par_schema(schema_name):
            raise ValueError("Ce sous-domaine est déjà utilisé.")

        if self.domain_repo.domaine_existe(domain_principal):
            raise ValueError("Ce domaine existe déjà.")

        # Créer le tenant
        tenant = Tenant(
            schema_name=schema_name,
            nom=data['nom'],
            sous_domaine=data['sous_domaine'],
            type_licence=data.get('type_licence', 'essai'),
            statut='essai',
            date_expiration=timezone.now() + timedelta(days=30),
            couleur_primaire=data.get('couleur_primaire', '#E91E63'),
            couleur_secondaire=data.get('couleur_secondaire', '#D8B26E'),
        )
        tenant.save()  # Déclenche la création du schéma PostgreSQL

        # Créer le domaine principal
        self.domain_repo.creer(
            tenant=tenant,
            domain=domain_principal,
            is_primary=True
        )

        # Domaine local pour les tests (développement uniquement)
        from django.conf import settings
        if settings.DEBUG:
            self.domain_repo.creer(
                tenant=tenant,
                domain=domain_local,
                is_primary=False
            )

        return tenant

    def activer(self, tenant_id, duree_jours=30):
        tenant = self.obtenir_tenant(tenant_id)
        self.tenant_repo.modifier(tenant, {
            'statut': 'actif',
            'date_expiration': timezone.now() + timedelta(days=duree_jours)
        })
        return tenant

    def suspendre(self, tenant_id):
        tenant = self.obtenir_tenant(tenant_id)
        if tenant.statut == 'suspendu':
            raise ValueError("Ce salon est déjà suspendu.")
        self.tenant_repo.modifier(tenant, {'statut': 'suspendu'})
        return tenant

    def debloquer(self, tenant_id):
        tenant = self.obtenir_tenant(tenant_id)
        if tenant.statut != 'suspendu':
            raise ValueError("Ce salon n'est pas suspendu.")
        self.tenant_repo.modifier(tenant, {'statut': 'actif'})
        return tenant

    def prolonger_essai(self, tenant_id, jours_supplementaires):
        tenant = self.obtenir_tenant(tenant_id)
        if tenant.statut not in ['essai', 'expire']:
            raise ValueError("La prolongation n'est possible que pour un essai ou un compte expiré.")

        nouvelle_expiration = timezone.now() + timedelta(days=jours_supplementaires)
        self.tenant_repo.modifier(tenant, {
            'statut': 'essai',
            'date_expiration': nouvelle_expiration
        })
        return tenant

    def modifier_licence(self, tenant_id, type_licence, duree_jours):
        tenant = self.obtenir_tenant(tenant_id)
        self.tenant_repo.modifier(tenant, {
            'type_licence': type_licence,
            'statut': 'actif',
            'date_expiration': timezone.now() + timedelta(days=duree_jours)
        })
        return tenant

    def associer_domaine_custom(self, tenant_id, domaine_custom):
        tenant = self.obtenir_tenant(tenant_id)

        if self.domain_repo.domaine_existe(domaine_custom):
            raise ValueError("Ce domaine est déjà associé à un salon.")

        # Supprimer l'ancien domaine custom si existant
        self.domain_repo.supprimer_custom(tenant)

        # Créer le nouveau domaine custom
        self.domain_repo.creer(
            tenant=tenant,
            domain=domaine_custom,
            is_primary=False
        )

        self.tenant_repo.modifier(tenant, {'domaine_custom': domaine_custom})
        return tenant

    def verifier_expirations(self):
        """
        À appeler via une tâche cron — suspend automatiquement
        les tenants expirés (section 3.11 du CDC).
        """
        maintenant = timezone.now()
        tenants_expires = Tenant.objects.filter(
            statut__in=['actif', 'essai'],
            date_expiration__lte=maintenant
        ).exclude(schema_name='public')

        count = 0
        for tenant in tenants_expires:
            self.tenant_repo.modifier(tenant, {'statut': 'expire'})
            count += 1

        return count
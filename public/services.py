from django.utils import timezone
from datetime import timedelta
from tenants.models import Tenant
from django.db import transaction, connection
from django.contrib.auth import get_user_model
from rest_framework_simplejwt.tokens import AccessToken
from django.conf import settings
from django_tenants.utils import schema_context
from .repository import TenantAdminRepository, DomainAdminRepository
from dateutil.relativedelta import relativedelta
from core.journal_mixin import journaliser_action

from tenants.models import JournalImpersonnalisation
from tenants.journal_service import JournalPlateformeService

User = get_user_model()


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
    
    def obtenir_tenant_par_sous_domaine(self, sous_domaine):
        tenant = self.tenant_repo.par_sous_domaine(sous_domaine)
        if tenant is None:
            raise ValueError("Salon introuvable.")
        return tenant

    def statistiques(self):
        return self.tenant_repo.statistiques()
    
    def _calculer_date_expiration(self, type_licence):
        """
        Calcule la date de fin exacte en fonction de la formule choisie.
        Utilise relativedelta pour une précision parfaite sur les mois et les années.
        """
        maintenant = timezone.now()
    
        # Configuration des durées
        DURATIONS = {
            'essai': relativedelta(months=1),       # 1 mois
            'mensuel': relativedelta(months=1),     # 1 mois
            'trimestriel': relativedelta(months=3),  # 3 mois
            'semestriel': relativedelta(months=6),   # 6 mois
            'annuel': relativedelta(years=1),        # 1 an
        }
    
        # Cas particulier pour "Illimité"
        if type_licence == 'illimite':
            return None  # Représente 'Pour toujours' (nécessite null=True sur votre champ de modèle)
            # Fallback si votre modèle exige une date : return maintenant + relativedelta(years=100)

        # Récupère la durée correspondante ou applique 1 mois d'essai par sécurité si non trouvé
        duree = DURATIONS.get(type_licence)
    
        return maintenant + duree
    
    def _creer_proprietaire(self, tenant, data):
        """
        Crée le compte propriétaire + son profil Personnel dans le schéma du tenant.
        Doit s'exécuter APRÈS tenant.save() (schéma + migrations déjà créés).
        """
        from apps.authentication.models import Utilisateur
        from apps.authentication.models import Personnel  # adapte le chemin réel
        from django.utils import timezone

        with schema_context(tenant.schema_name):
            utilisateur = Utilisateur.objects.create_user(
                email=data['proprietaire_email'],
                password=data['proprietaire_mot_de_passe'],
                role='proprietaire',
                tenant=tenant,
            )

            Personnel.objects.create(
                tenant=tenant,
                utilisateur=utilisateur,
                nom=data['proprietaire_nom'],
                prenom=data['proprietaire_prenom'],
                date_entree=timezone.now().date(),
                statut='actif',
            )

    @journaliser_action('creation_tenant')
    def creer_tenant(self, data, utilisateur=None):
        schema_name = data['sous_domaine'].lower().replace('-', '_')
        domain_principal = f"{data['sous_domaine']}.monsaas.cm"
        domain_local = f"{data['sous_domaine']}.localhost"

        # Vérifications
        if self.tenant_repo.par_schema(schema_name):
            raise ValueError("Ce sous-domaine est déjà utilisé.")

        if self.domain_repo.domaine_existe(domain_principal):
            raise ValueError("Ce domaine existe déjà.")
        
        # 1. Calcul dynamique du statut et de l'expiration
        type_licence = data.get('type_licence', 'essai')
        formule = data.get('formule', 'essai')
        date_expiration = self._calculer_date_expiration(type_licence)

        # 2. Sécurisation globale via une transaction atomique
        try:
            with transaction.atomic():
                # Créer le tenant
                tenant = Tenant(
                    schema_name=schema_name,
                    nom=data['nom'],
                    sous_domaine=data['sous_domaine'],
                    type_licence=type_licence,
                    formule=formule,
                    statut=data.get('statut', 'essai'),
                    date_expiration=date_expiration,
                    couleur_primaire=data.get('couleur_primaire', '#E91E63'),
                    couleur_secondaire=data.get('couleur_secondaire', '#D8B26E'),
                )
                # Déclenche la création du schéma PostgreSQL et l'exécution des migrations
                tenant.save()  

                # Créer le domaine principal
                self.domain_repo.creer(
                    tenant=tenant,
                    domain=domain_principal,
                    is_primary=True
                )

                # Domaine local pour les tests (développement uniquement)
                if settings.DEBUG:
                    self.domain_repo.creer(
                        tenant=tenant,
                        domain=domain_local,
                        is_primary=False
                    )

                # Création du compte propriétaire directement dans le schéma du tenant
                # Si cette fonction lève une exception, la transaction s'annule immédiatement !
                self._creer_proprietaire(tenant, data)

                return tenant

        except Exception as e:
            # 3. 🚨 NETTOYAGE CRITIQUE POUR MULTI-TENANT
            # Si un problème survient, Django va rollback l'insertion de la ligne Tenant dans la table publique.
            # Mais pour être absolument certain que le schéma PostgreSQL orphelin ne reste pas sur votre serveur :
            self._nettoyer_schema_orphelin(schema_name)
        
            # On propage l'erreur d'origine pour que le contrôleur/API la reçoive et l'affiche au frontend
            raise e

    def _nettoyer_schema_orphelin(self, schema_name):
        """
        Supprime manuellement le schéma PostgreSQL si la création a échoué à mi-chemin
        pour éviter d'encombrer la base de données avec des schémas fantômes.
        """
        try:
            with connection.cursor() as cursor:
                # On force la suppression du schéma et de tout son contenu (tables, types...)
                cursor.execute(f"DROP SCHEMA IF EXISTS {schema_name} CASCADE;")
        except Exception as db_err:
            # On log l'erreur discrètement pour ne pas masquer l'erreur principale du plantage utilisateur
            print(f"Erreur lors du nettoyage de sécurité du schéma {schema_name}: {db_err}")

    # NOTE : la fonction d'activation de licence réellement utilisée par
    # SuperAdminActiverView est `modifier_licence()`, plus bas dans ce fichier.
    # (Une fonction `activer()` dupliquée existait ici sans jamais être
    # appelée nulle part — supprimée pour éviter la confusion.)

    @journaliser_action('suspension')
    def suspendre(self, tenant_id):
        tenant = self.obtenir_tenant(tenant_id)
        if tenant.statut == 'suspendu':
            raise ValueError("Cette entreprise est déjà suspendue.")
        # Mémorise l'état actuel avant de modifier
        tenant.statut_avant_suspension = tenant.statut
        self.tenant_repo.modifier(tenant, {'statut': 'suspendu'})
        tenant.save()
        return tenant

    @journaliser_action('reactivation')
    def debloquer(self, tenant_id):
        tenant = self.obtenir_tenant(tenant_id)
        if tenant.statut != 'suspendu':
            raise ValueError("Ce tenant n'est pas suspendu.")
        # Vérification critique: Vérifier si la licence est toujours valide
        if tenant.date_expiration and tenant.date_expiration < timezone.now():
            # Refut du changement de statut, demander à passer par l'activation d'une licence
            raise LicenceExpireeError("La licence a expiré pendant la suspension. Veuillez activer une licence.")
        # restaurer le statut plutôt que de forcer un statut actif en dur
        tenant.statut = tenant.statut_avant_suspension or 'actif' # Cas où le statut avant suspension est vide
        # Nettoyage du statut avant suspension
        tenant.statut_avant_suspension = None
        tenant.save()
        return tenant

    @journaliser_action('prolongation_essai')
    def prolonger_essai(self, tenant_id, jours_supplementaires):
        """
        Usage : Super Admin accorde plus de temps à un prospect.
        Condition : type_licence == 'essai' uniquement.
        Effet : repousse date_expiration, statut reste 'essai'.
        """
        tenant = self.obtenir_tenant(tenant_id)
        if tenant.type_licence != 'essai':
            raise ValueError("Cette fonction est réservée aux comptes en période d'essai.")

        maintenant = timezone.now()
        base = (
            tenant.date_expiration
            if tenant.date_expiration and tenant.date_expiration > maintenant
            else maintenant
        )
        nouvelle_expiration = base + timedelta(days=jours_supplementaires)

        self.tenant_repo.modifier(tenant, {
            'date_expiration': nouvelle_expiration
            # statut inchangé — reste 'essai' ou 'actif' selon ce qu'il était
        })
        return tenant

    @journaliser_action('ajout__jours_licence')
    def ajouter_jours_licence(self, tenant_id, jours_supplementaires):
        """
        Usage : geste commercial, compensation panne, ajustement manuel.
        Condition : tout type sauf 'illimite' (pas de date d'expiration).
        Effet : repousse date_expiration, réactive le compte si suspendu/expiré.
        """
        tenant = self.obtenir_tenant(tenant_id)
        if tenant.type_licence == 'illimite':
            raise ValueError("Un compte illimité n'a pas de date d'expiration à prolonger.")

        maintenant = timezone.now()
        base = (
            tenant.date_expiration
            if tenant.date_expiration and tenant.date_expiration > maintenant
            else maintenant
        )
        nouvelle_expiration = base + timedelta(days=jours_supplementaires)

        nouveau_statut = 'actif' if tenant.statut in ['suspendu', 'expire'] else tenant.statut

        self.tenant_repo.modifier(tenant, {
            'date_expiration': nouvelle_expiration,
            'statut': nouveau_statut
        })
        return tenant

    @journaliser_action('activer_licence')
    def modifier_licence(self, tenant_id, type_licence, formule):
        tenant = self.obtenir_tenant(tenant_id)
        nouvelle_expiration = self._calculer_date_expiration(type_licence)
        self.tenant_repo.modifier(tenant, {
            'type_licence': type_licence,
            'formule': formule,
            'statut': 'actif',
            'date_expiration': nouvelle_expiration
        })
        return tenant

    @journaliser_action('domaine_custom')
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
    
    def lister_expirant_bientot(self, jours=25):
        return self.tenant_repo.expirant_bientot(jours=jours)
    

class LicenceExpireeError(Exception):
    """Levée quand une réactivation est refusée car la licence a expiré."""
    pass


# IMPERSONNALISATION
class ImpersonnalisationService:

    def impersonnaliser(self, super_admin, tenant_domaine, request):
        try:
            tenant = Tenant.objects.get(sous_domaine=tenant_domaine)
        except Tenant.DoesNotExist:
            raise ValueError("Tenant introuvable.")

        if tenant.statut in ['suspendu', 'expire']:
            raise ValueError(
                "Impossible d'accéder au backoffice d'un tenant suspendu ou expiré."
            )

        try:
            proprietaire = User.objects.get(tenant=tenant, role='proprietaire')
        except User.DoesNotExist:
            raise ValueError("Aucune propriétaire trouvée pour ce tenant.")

        token = AccessToken.for_user(proprietaire)
        token.set_exp(lifetime=timedelta(hours=2))
        token['impersonnalisation'] = True
        token['super_admin_id'] = super_admin.id

        ip = JournalPlateformeService._extraire_ip(request)
        JournalImpersonnalisation.objects.create(
            super_admin=super_admin,
            tenant=tenant,
            proprietaire_email=proprietaire.email,
            adresse_ip=ip,
            user_agent=request.META.get('HTTP_USER_AGENT', '')
        )

        JournalPlateformeService.enregistrer(
            super_admin=super_admin,
            type_action='impersonnalisation',
            tenant=tenant,
            details={'proprietaire_email': proprietaire.email},
            request=request
        )

        return {
            'access': str(token),
            'tenant_sous_domaine': tenant.sous_domaine,
            'tenant_nom': tenant.nom,
            'proprietaire_email': proprietaire.email,
        }
from rest_framework.views import APIView
from django.utils import timezone
from core.responses import success, error, created, not_found
from core.permissions import EstSuperAdmin
from rest_framework.permissions import IsAuthenticated
from .services import SuperAdminService, LicenceExpireeError
from .serializers import (
    TenantAdminSerializer, TenantCreateSerializer, ActiverLicenceSerializer,
    ProlongerEssaiSerializer, DomainCustomSerializer, StatistiquesSerializer
)
from tenants.models import Tenant
from tenants.journal_service import JournalPlateformeService
from .services import ImpersonnalisationService
from tenants.services import TenantService
from tenants.serializers import TenantPublicSerializer
from drf_spectacular.utils import extend_schema
from rest_framework.permissions import AllowAny

# =============================================
# ROUTES PUBLIQUES (sans authentification)
# =============================================
class HealthCheckView(APIView):
    """
    Endpoint de vérification que l'API fonctionne correctement.
    """

    def get(self, request):
        return success(
            data = {
                'status': 'ok',
                'timestamp': timezone.now(),
            },
            message="L'API fonctionne correctement"
        )


class TenantInfoView(APIView):
    """
    Endpoint public — retourne les infos de personnalisation
    du salon courant sans authentification.
    """
    permission_classes = [AllowAny]

    @extend_schema(responses=TenantPublicSerializer)
    def get(self, request):
        service = TenantService()
        try:
            tenant = service.obtenir_courant()
            return success(
                data=TenantPublicSerializer(tenant).data,
                message="Informations du salon"
            )
        except ValueError as e:
            return error(message=str(e), status_code=404)
        


# =============================================
# ROUTES SUPER ADMIN (authentification requise)
# =============================================

class SuperAdminTableauDeBordView(APIView):
    permission_classes = [IsAuthenticated, EstSuperAdmin]

    @extend_schema(responses=StatistiquesSerializer)
    def get(self, request):
        service = SuperAdminService()
        stats = service.statistiques()
        return success(data=stats, message="Tableau de bord Super Admin")


class SuperAdminTenantListCreateView(APIView):
    permission_classes = [IsAuthenticated, EstSuperAdmin]

    @extend_schema(responses=TenantAdminSerializer(many=True))
    def get(self, request):
        service = SuperAdminService()
        statut = request.query_params.get('statut')
        tenants = service.lister_tenants(statut=statut)
        return success(
            data=TenantAdminSerializer(tenants, many=True).data,
            message="Liste des salons"
        )

    @extend_schema(request=TenantAdminSerializer, responses=TenantAdminSerializer)
    def post(self, request):
        serializer = TenantCreateSerializer(data=request.data)
        if not serializer.is_valid():
            return error(message="Données invalides", errors=serializer.errors)

        service = SuperAdminService()
        try:
            tenant = service.creer_tenant(
                serializer.validated_data,
                utilisateur=request.user
            )
            return created(
                data=TenantAdminSerializer(tenant).data,
                message="Salon créé avec succès"
            )
        except ValueError as e:
            return error(message=str(e), status_code=400)


class SuperAdminTenantDetailView(APIView):
    permission_classes = [IsAuthenticated, EstSuperAdmin]

    @extend_schema(responses=TenantAdminSerializer)
    def get(self, request, sous_domaine):
        service = SuperAdminService()
        try:
            tenant = service.obtenir_tenant_par_sous_domaine(sous_domaine)
            return success(
                data=TenantAdminSerializer(tenant).data,
                message="Salon trouvé"
            )
        except ValueError as e:
            return not_found(str(e))


class SuperAdminActiverView(APIView):
    permission_classes = [IsAuthenticated, EstSuperAdmin]

    @extend_schema(request=ActiverLicenceSerializer, responses=TenantAdminSerializer)
    def post(self, request, tenant_id):
        serializer = ActiverLicenceSerializer(data=request.data)
        if not serializer.is_valid():
            return error(message="Données invalides", errors=serializer.errors)

        service = SuperAdminService()
        try:
            tenant = service.modifier_licence(
                tenant_id,
                serializer.validated_data['type_licence'],
                serializer.validated_data['formule'],
            )
            return success(
                data=TenantAdminSerializer(tenant).data,
                message="Licence activée"
            )
        except ValueError as e:
            return error(message=str(e), status_code=400)


class SuperAdminSuspendreView(APIView):
    permission_classes = [IsAuthenticated, EstSuperAdmin]

    @extend_schema(request=None, responses=TenantAdminSerializer)
    def post(self, request, tenant_id):
        service = SuperAdminService()
        try:
            tenant = service.suspendre(tenant_id)
            return success(
                data=TenantAdminSerializer(tenant).data,
                message="Salon suspendu"
            )
        except ValueError as e:
            return error(message=str(e), status_code=400)


class SuperAdminDebloquerView(APIView):
    permission_classes = [IsAuthenticated, EstSuperAdmin]

    @extend_schema(request=None, responses=TenantAdminSerializer)
    def post(self, request, tenant_id):
        service = SuperAdminService()
        try:
            tenant = service.debloquer(tenant_id)
            return success(
                data=TenantAdminSerializer(tenant).data,
                message="Salon débloqué"
            )
        except LicenceExpireeError as e:
            return error(message=str(e), status_code=409)
        except ValueError as e:
            return error(message=str(e), status_code=400)


class SuperAdminProlongerEssaiView(APIView):
    permission_classes = [IsAuthenticated, EstSuperAdmin]

    @extend_schema(request=ProlongerEssaiSerializer, responses=TenantAdminSerializer)
    def post(self, request, tenant_id):
        serializer = ProlongerEssaiSerializer(data=request.data)
        if not serializer.is_valid():
            return error(message="Données invalides", errors=serializer.errors)

        service = SuperAdminService()
        try:
            tenant = service.prolonger_essai(
                tenant_id,
                serializer.validated_data['jours_supplementaires']
            )
            return success(
                data=TenantAdminSerializer(tenant).data,
                message="Période d'essai prolongée"
            )
        except ValueError as e:
            return error(message=str(e), status_code=400)
        
class SuperAdminAjouterJoursLicenceView(APIView):
    permission_classes = [IsAuthenticated, EstSuperAdmin]

    @extend_schema(request=ProlongerEssaiSerializer, responses=TenantAdminSerializer)
    def post(self, request, tenant_id):
        serializer = ProlongerEssaiSerializer(data=request.data)
        if not serializer.is_valid():
            return error(message="Données invalides", errors=serializer.errors)

        service = SuperAdminService()
        try:
            tenant = service.ajouter_jours_licence(
                tenant_id,
                serializer.validated_data['jours_supplementaires']
            )
            return success(
                data=TenantAdminSerializer(tenant).data,
                message="Période d'activation revue à la hausse"
            )
        except ValueError as e:
            return error(message=str(e), status_code=400)


class SuperAdminDomainCustomView(APIView):
    permission_classes = [IsAuthenticated, EstSuperAdmin]

    @extend_schema(request=DomainCustomSerializer, responses=TenantAdminSerializer)
    def post(self, request, tenant_id):
        serializer = DomainCustomSerializer(data=request.data)
        if not serializer.is_valid():
            return error(message="Données invalides", errors=serializer.errors)

        service = SuperAdminService()
        try:
            tenant = service.associer_domaine_custom(
                tenant_id,
                serializer.validated_data['domaine_custom']
            )
            return success(
                data=TenantAdminSerializer(tenant).data,
                message="Domaine personnalisé associé"
            )
        except ValueError as e:
            return error(message=str(e), status_code=400)


class SuperAdminVerifierExpirationsView(APIView):
    permission_classes = [IsAuthenticated, EstSuperAdmin]

    @extend_schema(request=None, responses=None)
    def post(self, request):
        service = SuperAdminService()
        count = service.verifier_expirations()
        return success(
            data={'tenants_expires': count},
            message=f"{count} salon(s) suspendu(s) pour expiration"
        )
    
class SuperAdminExpirantBientotView(APIView):
    permission_classes = [IsAuthenticated, EstSuperAdmin]

    @extend_schema(responses=TenantAdminSerializer(many=True))
    def get(self, request):
        service = SuperAdminService()
        jours = int(request.query_params.get('jours', 25))
        tenants = service.lister_expirant_bientot(jours=jours)
        return success(
            data=TenantAdminSerializer(tenants, many=True).data,
            message="Salons expirant bientôt"
        )
    

class SuperAdminImpersonnaliserView(APIView):
    permission_classes = [IsAuthenticated, EstSuperAdmin]

    @extend_schema(responses=None)
    def post(self, request, sous_domaine):
        service = ImpersonnalisationService()
        try:
            resultat = service.impersonnaliser(request.user, sous_domaine, request)
            return success(data=resultat, message="Accès support activé")
        except ValueError as e:
            return error(message=str(e), status_code=400)


class SuperAdminJournalTenantView(APIView):
    permission_classes = [IsAuthenticated, EstSuperAdmin]

    def get(self, request, tenant_id):
        try:
            tenant = Tenant.objects.get(id=tenant_id)
        except Tenant.DoesNotExist:
            return error(message="Tenant introuvable.", status_code=404)

        JournalPlateformeService.enregistrer(
            super_admin=request.user,
            type_action='consultation_journal',
            tenant=tenant,
            details={
                'ressource': request.query_params.get('ressource'),
                'type_action': request.query_params.get('type_action'),
            },
            request=request
        )

        data = JournalPlateformeService.lire_journal_tenant(
            tenant=tenant,
            ressource=request.query_params.get('ressource'),
            type_action=request.query_params.get('type_action'),
        )
        return success(data=data, message=f"Journal de {tenant.nom}")


class SuperAdminJournalPlateformeView(APIView):
    """Journal des actions du Super Admin lui-même — traçabilité globale."""
    permission_classes = [IsAuthenticated, EstSuperAdmin]

    def get(self, request):
        from tenants.models import JournalPlateforme
        from .serializers import JournalPlateformeSerializer

        tenant_id = request.query_params.get('tenant_id')
        type_action = request.query_params.get('type_action')

        tenant = None
        if tenant_id:
            tenant = Tenant.objects.filter(id=tenant_id).first()

        actions = JournalPlateformeService.liste_plateforme(
            tenant=tenant,
            type_action=type_action
        )
        return success(data=JournalPlateformeSerializer(actions, many=True).data)
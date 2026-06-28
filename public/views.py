from rest_framework.views import APIView
from django.utils import timezone
from core.responses import success, error, created, not_found
from core.permissions import EstSuperAdmin
from rest_framework.permissions import IsAuthenticated
from .services import SuperAdminService
from .serializers import (
    TenantAdminSerializer, TenantCreateSerializer, ActiverLicenceSerializer,
    ProlongerEssaiSerializer, DomainCustomSerializer, StatistiquesSerializer
)
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
    def get(self, request, tenant_id):
        service = SuperAdminService()
        try:
            tenant = service.obtenir_tenant(tenant_id)
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
                serializer.validated_data['duree_jours']
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